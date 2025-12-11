"""
rag_engine.py:
Implements the core Retrieval Augmented Generation (RAG) chain.
It loads the persistent vector store, sets up the LLM, and combines them
to answer user queries using the knowledge grounded in the IRC/MoRTH data.
Additionally, integrates LDA topic modeling for enhanced retrieval.
"""
import os
import pickle
from dotenv import load_dotenv
import random # Added import for random, used in the previous conversation's update

# LangChain and Google Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma

# Topic Modeling Imports
from gensim.models import LdaModel

# Local Imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_processor import preprocess_text

# Load environment variables (especially GEMINI_API_KEY)
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
VECTOR_STORE_PATH = "data/vectorstore/"
LDA_MODEL_PATH = os.path.join(VECTOR_STORE_PATH, "lda_model.pkl")
# Ensure these match the models used in data_processor.py
EMBEDDING_MODEL = "models/text-embedding-004"
GENERATION_MODEL = "gemini-2.5-flash"

# --- RAG Prompt Template ---
# This system prompt guides the LLM on its persona and role
RAG_PROMPT_TEMPLATE = """
You are RoadSafetyGPT, a specialized AI assistant for Indian road safety, traffic, and infrastructure codes.
Your knowledge is strictly grounded in the provided context, which includes documents from the Ministry of Road Transport and Highways (MoRTH),
Indian Road Congress (IRC), and the National Crime Records Bureau (NCRB).

1. Answer the user's question concisely and accurately based ONLY on the following context.
2. If the context does not contain the answer to the specific question, state clearly that the information is not available in the provided documents. Do not provide any additional information, explanations, or related guidelines.
3. Be professional, direct, and reference specific codes or figures where possible.

CONTEXT:
{context}

QUESTION: {question}
ANSWER:
"""

class RAGEngine:
    """
    Manages the RAG chain for retrieving information from the specialized knowledge base.
    """
    def __init__(self, vector_store=None):
        """Initializes the LLM, Embeddings, and loads the Vector Store."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")

        # 1. Initialize LLM for generating responses
        from langchain_core.globals import set_verbose, set_debug, set_llm_cache
        set_verbose(False)
        set_debug(False)
        set_llm_cache(None)
        self.llm = ChatGoogleGenerativeAI(
            model=GENERATION_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1 # Keep temperature low for factual accuracy
        )

        # 2. Initialize Embeddings (must match the model used for persistence)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GEMINI_API_KEY)

        # 3. Load the persistent vector store (ChromaDB) or use provided one
        if vector_store:
            self.vector_store = vector_store
            print("Using provided vector store.")
        else:
            try:
                self.vector_store = Chroma(
                    persist_directory=VECTOR_STORE_PATH,
                    embedding_function=self.embeddings
                )
                print("Vector Store successfully loaded from disk.")
            except Exception as e:
                # This happens if the directory is empty or improperly structured
                print(f"Error loading vector store: {e}")
                print("Run 'python src/data_processor.py' first to build the store.")
                self.vector_store = None # Set to None to prevent usage

        # 4. Create the retriever object
        # The retriever is responsible for finding the most relevant chunks
        if self.vector_store:
            # Search the top 3 most relevant documents (chunks)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        else:
            self.retriever = None

        # 5. Load LDA Model for topic enhancement
        try:
            with open(LDA_MODEL_PATH, 'rb') as f:
                self.lda_model = pickle.load(f)
            print("LDA Model successfully loaded from disk.")
        except Exception as e:
            print(f"Error loading LDA model: {e}")
            print("Run 'python src/data_processor.py' first to train the model.")
            self.lda_model = None

        # 6. Define the RAG Chain
        self.prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        # The chain combines context retrieval, prompting, and generation
        # format_docs is a helper to clean up the document format for the prompt
        self.rag_chain = (
            {"context": self.retriever | self._format_docs_with_topics, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        print("RAG Engine successfully initialized.")

    def _format_docs(self, docs):
        """Helper function to format documents into a single string for the prompt."""
        return "\n\n".join(doc.page_content for doc in docs)

    def _format_docs_with_topics(self, docs):
        """Helper function to format documents with topic summaries for enhanced context."""
        formatted_docs = []
        for doc in docs:
            content = doc.page_content
            if self.lda_model:
                # Preprocess content to match training tokenization
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from src.data_processor import preprocess_text
                tokens = preprocess_text(content)[:50]  # Use first 50 tokens
                bow = self.lda_model.id2word.doc2bow(tokens)
                topic_dist = self.lda_model[bow]
                if topic_dist:
                    dominant_topic = max(topic_dist, key=lambda x: x[1])[0]
                    topic_words = self.lda_model.show_topic(dominant_topic, topn=5)
                    topic_summary = f"Topic {dominant_topic + 1}: " + ", ".join([word for word, _ in topic_words])
                    content = f"[Topic Summary: {topic_summary}]\n{content}"
            formatted_docs.append(content)
        return "\n\n".join(formatted_docs)

    def query(self, user_question: str) -> tuple[str, list]:
        """
        Executes the RAG chain with the user's question.
        Always provides an answer by using the retrieved context in a comprehensive LLM query.

        Args:
            user_question: The question asked by the user.

        Returns:
            A tuple of (generated answer, list of retrieved docs), using context if available.
        """
        if not self.vector_store:
            return "RAG Engine is not initialized. Please ensure the vector store is built first.", []

        print(f"\nProcessing query: {user_question}")

        try:
            # Retrieve context from vector store
            docs = self.retriever.invoke(user_question)
            context = self._format_docs_with_topics(docs)

            # Enhanced prompt for structured response
            comprehensive_prompt = f"""
You are RoadSafetyGPT, a specialized AI assistant for Indian road safety, traffic, and infrastructure codes.
Your knowledge is grounded in IRC, MoRTH, and NCRB documents. Use the provided context if relevant, otherwise provide a comprehensive answer based on standard practices and guidelines.

Structure your response with the following sections if applicable:
- **Intervention**: Recommended actions or guidelines.
- **Evidence**: Supporting facts or references from documents.
- **Severity**: Potential risks or importance level.

CONTEXT:
{context}

QUESTION: {user_question}
ANSWER:
"""
            response = self.llm.invoke(comprehensive_prompt)
            answer = response.content.strip()
            # Remove the "However," line if it starts with "The provided context does not contain..."
            if answer.startswith("The provided context does not contain"):
                lines = answer.split('\n')
                if len(lines) > 1 and lines[1].strip().startswith("However,"):
                    answer = '\n'.join(lines[2:]).strip()
            return answer, docs
        except Exception as e:
            # Handle potential API errors or other runtime issues
            return f"An error occurred during query execution: {e}", []


# --- Example Usage ---
if __name__ == "__main__":
    try:
        engine = RAGEngine()

        # Test Query 1: Factual question that should be grounded in the IRC documents
        query_1 = "What are the recommended materials for a kerb ramp according to IRC standards?"
        response_1 = engine.query(query_1)
        print("\n--- Response 1 ---")
        print(response_1)

        # Test Query 2: A question that might require data from the NCRB/MoRTH report
        query_2 = "Summarize the key types of road accidents based on vehicle type for the year 2023."
        response_2 = engine.query(query_2)
        print("\n--- Response 2 ---")
        print(response_2)
        
    except ValueError as e:
        print(f"Initialization Error: {e}")
    except Exception as e:
        print(f"A general error occurred: {e}")
