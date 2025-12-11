"""
data_processor.py:
Reads raw documents from data/raw/, chunks them, embeds them using a Google model,
and saves the resulting vector store (index) to data/vectorstore/.
Additionally, performs text extraction, TF-IDF vectorization, and LDA topic modeling.
"""
import os
import pickle
from dotenv import load_dotenv

# LangChain Imports for Document Processing
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Topic Modeling Imports
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models
from gensim.models import LdaModel
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import re

# Load environment variables (especially GEMINI_API_KEY)
load_dotenv()

# --- Configuration ---
RAW_DATA_PATH = "data/raw/"
VECTOR_STORE_PATH = "data/vectorstore/"
LDA_MODEL_PATH = os.path.join(VECTOR_STORE_PATH, "lda_model.pkl")
DICTIONARY_PATH = os.path.join(VECTOR_STORE_PATH, "lda_dictionary.pkl")
COUNT_VECTORIZER_PATH = os.path.join(VECTOR_STORE_PATH, "count_vectorizer.pkl")
# Use a good embedding model
EMBEDDING_MODEL = "text-embedding-004"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# LDA Configuration
NUM_TOPICS = 3  # Based on your Colab output
MAX_FEATURES = 5000  # Bag-of-words features

def load_documents(directory_path: str):
    """Loads all PDF files from the specified directory."""
    documents = []
    print(f"Loading documents from: {directory_path}")
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory_path, filename)
            try:
                # Use PyPDFLoader to load the content of the PDF
                loader = PyPDFLoader(filepath)
                documents.extend(loader.load())
                print(f"Successfully loaded {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return documents

def split_documents(documents):
    """Splits documents into smaller, overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Original documents split into {len(chunks)} chunks.")
    return chunks

def preprocess_text(text):
    """Preprocesses text for topic modeling: lowercase, tokenize, remove punctuation and stop words."""
    # Download NLTK data if not present
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
    return tokens

def extract_text_from_documents(documents):
    """Extracts raw text from LangChain documents for topic modeling."""
    texts = []
    for doc in documents:
        texts.append(doc.page_content)
    print(f"Extracted text from {len(texts)} documents.")
    return texts

def train_lda_model(texts):
    """Trains LDA model using bag-of-words vectorization."""
    print("Starting LDA training...")

    # Preprocess texts
    processed_texts = [preprocess_text(text) for text in texts]

    # Create dictionary from processed texts
    dictionary = corpora.Dictionary(processed_texts)
    dictionary.filter_extremes(no_below=2, no_above=0.5)

    # Create corpus from processed texts using dictionary
    corpus = [dictionary.doc2bow(text) for text in processed_texts]

    # 1. Bag-of-Words Vectorization (for saving, not used in LDA)
    vectorizer = CountVectorizer(max_features=MAX_FEATURES, stop_words='english')
    bow_matrix = vectorizer.fit_transform(texts)  # Use original texts for sklearn vectorizer
    print(f"Bag-of-words matrix shape: {bow_matrix.shape}")

    # 3. Train LDA Model
    lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=NUM_TOPICS, random_state=42, passes=10)
    print("LDA Model Training Complete.")

    # Print top words per topic (similar to your Colab output)
    print(f"\nTop 10 words per {NUM_TOPICS} Topics:")
    for i in range(NUM_TOPICS):
        words = lda_model.show_topic(i, topn=10)
        word_str = " ".join([word for word, _ in words])
        print(f"  Topic {i+1}: {word_str}")

    return lda_model, dictionary, vectorizer

def save_lda_model(lda_model, dictionary, vectorizer):
    """Saves the LDA model, dictionary, and vectorizer to disk."""
    with open(LDA_MODEL_PATH, 'wb') as f:
        pickle.dump(lda_model, f)
    with open(DICTIONARY_PATH, 'wb') as f:
        pickle.dump(dictionary, f)
    with open(COUNT_VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"LDA model and components saved to {VECTOR_STORE_PATH}")

def build_vector_store(chunks):
    """Embeds the chunks and creates a persistent Chroma vector store."""

    # 1. Initialize the embedding model
    # Note: Requires the GEMINI_API_KEY environment variable to be set
    embeddings = GoogleGenerativeAIEmbeddings(model=f"models/{EMBEDDING_MODEL}", google_api_key=os.getenv("GEMINI_API_KEY"))
    print(f"Using embedding model: {EMBEDDING_MODEL}")

    # 2. Create the Chroma vector store and persist it
    # This process calculates embeddings for all chunks and writes them to disk
    print(f"Starting vector store creation in {VECTOR_STORE_PATH}...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    db.persist() # Explicitly persist the collection (optional, but good practice)
    print("Vector store successfully built and saved to disk!")
    return db

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        print("Please set your API key to run the embedding process.")
    else:
        # Create the vectorstore directory if it doesn't exist
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

        # 1. Load Raw Documents
        raw_documents = load_documents(RAW_DATA_PATH)

        if raw_documents:
            # 2. Extract Text for Topic Modeling
            document_texts = extract_text_from_documents(raw_documents)

            # 3. Train LDA Model
            lda_model, dictionary, vectorizer = train_lda_model(document_texts)

            # 4. Save LDA Model
            save_lda_model(lda_model, dictionary, vectorizer)

            # 5. Split Documents into Chunks
            document_chunks = split_documents(raw_documents)

            # 6. Build and Persist Vector Store
            vector_db = build_vector_store(document_chunks)
            print("\nProcessor script finished. Your vector store and LDA model are ready!")
        else:
            print("No documents found in data/raw/. Please check the directory.")
