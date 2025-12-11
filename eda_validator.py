"""
eda_validator.py:
Performs Exploratory Data Analysis (EDA) and validation checks on structured
data (e.g., CSVs containing accident records) before it is used for analysis
or multimodal handling.

Includes NLTK initialization to resolve environment-related 'undefined' errors.
"""
import pandas as pd
import numpy as np
import nltk
import os
from typing import Optional

# --- NLTK Data Download ---
# CRITICAL: This addresses the Pylance error 'nltk' is not defined by ensuring 
# the necessary NLTK corpora are downloaded before any NLTK function is called.
def setup_nltk():
    """Downloads required NLTK data if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except nltk.downloader.DownloadError:
        print("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except nltk.downloader.DownloadError:
        print("Downloading NLTK 'stopwords'...")
        nltk.download('stopwords', quiet=True)
    print("NLTK setup complete.")

class EDAValidator:
    """
    A utility class for cleaning, validating, and performing basic EDA
    on structured data (Pandas DataFrames).
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.initial_shape = df.shape
        self.validation_report = {}

    def run_basic_checks(self) -> dict:
        """Checks for missing values, unique counts, and data types."""
        print("--- Running Basic Data Checks ---")
        report = {
            "initial_shape": self.initial_shape,
            "data_types": self.df.dtypes.apply(lambda x: x.name).to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "unique_counts": self.df.nunique().to_dict()
        }
        self.validation_report.update(report)
        return report

    def clean_column_names(self):
        """Standardizes column names to lowercase and replaces spaces with underscores."""
        self.df.columns = self.df.columns.str.lower().str.replace(' ', '_', regex=True)
        print("Column names standardized.")

    def identify_and_report_outliers(self, column: str, threshold: float = 3.0) -> Optional[pd.DataFrame]:
        """Identifies potential outliers using the Z-score method."""
        if column not in self.df.columns or self.df[column].dtype not in ['int64', 'float64']:
            print(f"Skipping outlier check: Column '{column}' not found or is non-numeric.")
            return None

        print(f"--- Checking Outliers for '{column}' ---")
        
        # Calculate Z-scores
        z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
        outliers = self.df[z_scores > threshold]
        
        print(f"Found {len(outliers)} potential outliers in '{column}' (Z > {threshold}).")
        
        self.validation_report[f'outliers_count_{column}'] = len(outliers)
        
        return outliers

    def analyze_text_column(self, column: str):
        """Performs basic text analysis (token counts, stopword removal concept)."""
        if column not in self.df.columns or self.df[column].dtype != 'object':
            print(f"Skipping text analysis: Column '{column}' not found or is not a string type.")
            return

        print(f"--- Running Text Analysis for '{column}' ---")
        
        # Ensure NLTK data is ready
        setup_nltk() 

        # Simple token count
        token_counts = self.df[column].astype(str).apply(lambda x: len(nltk.word_tokenize(x)))
        
        # Example of applying stopword removal (useful for creating better embeddings)
        stop_words = set(nltk.corpus.stopwords.words('english'))
        
        def remove_stopwords(text):
            words = nltk.word_tokenize(text)
            # Filter out stopwords and non-alphanumeric tokens
            filtered_words = [w for w in words if w.lower() not in stop_words and w.isalnum()]
            return " ".join(filtered_words)

        # Example application of the cleanup function:
        # self.df[f'{column}_cleaned'] = self.df[column].astype(str).apply(remove_stopwords)
        
        print(f"Average token count in '{column}': {token_counts.mean():.2f}")
        self.validation_report[f'avg_tokens_{column}'] = token_counts.mean()
        
    def generate_report(self):
        """Prints the final validation and EDA summary."""
        print("\n=======================================================")
        print("         FINAL DATA VALIDATION AND EDA REPORT          ")
        print("=======================================================")
        
        for key, value in self.validation_report.items():
            if isinstance(value, dict):
                print(f"\n--- {key.replace('_', ' ').title()} ---")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"- {key.replace('_', ' ').title()}: {value}")
        
        print("=======================================================")


# --- Example Usage ---
if __name__ == "__main__":
    # 1. Setup NLTK data once (optional, but good practice)
    setup_nltk()
    
    # 2. Create a dummy DataFrame mimicking accident data
    data = {
        'Accident_ID': range(100),
        'Year': np.random.randint(2020, 2024, 100),
        'Fatalities': np.random.randint(0, 5, 100),
        'Injury_Count': np.random.randint(0, 15, 100),
        'Road_Type': np.random.choice(['NH', 'SH', 'Other'], 100),
        'Description': [
            "Heavy rain caused a pile-up near the toll plaza.",
            "Two-wheeler skidded due to a pothole.",
            "Driver error leading to a minor collision.",
            "The truck overturned, blocking the highway.",
            "High speed incident. The driver was not wearing a seatbelt."
        ] * 20
    }
    # Introduce a few missing values and an outlier for demonstration
    data['Fatalities'][95] = 50 # Outlier
    data['Road_Type'][5] = np.nan # Missing value
    df_sample = pd.DataFrame(data)

    # 3. Initialize and run the validator
    validator = EDAValidator(df_sample)
    
    validator.clean_column_names()
    
    # 4. Run checks
    validator.run_basic_checks()
    validator.identify_and_report_outliers('fatalities')
    validator.analyze_text_column('description')
    
    # 5. Display report
    validator.generate_report()
