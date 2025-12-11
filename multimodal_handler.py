"""
multimodal_handler.py:
Handles image-to-text (multimodal) processing using the Gemini API.
This is used to analyze images of road signs, accident scenes, or infrastructure.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

# Load environment variables (especially GEMINI_API_KEY)
load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.0-flash"  # Use a multimodal model

class MultimodalHandler:
    """
    A class to handle image analysis and generate textual descriptions and insights.
    """
    def __init__(self):
        """Initializes the handler and checks for the API key."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to use the Gemini API.")
        genai.configure(api_key=GEMINI_API_KEY)
        # List available models for debugging
        try:
            models = genai.list_models()
            print("Available models:")
            for model in models:
                print(f"- {model.name}")
        except Exception as e:
            print(f"Error listing models: {e}")
        self.model = genai.GenerativeModel(MODEL_NAME)
        print(f"MultimodalHandler initialized. Using model: {MODEL_NAME}")

    def analyze_image(self, image_path: str, prompt: str) -> Optional[str]:
        """
        Sends an image and a text prompt to the Gemini API for analysis.

        Args:
            image_path: The local file path to the image to analyze.
            prompt: The text query instructing the model on what to look for.

        Returns:
            The generated textual analysis from the model, or None if an error occurs.
        """
        try:
            # Open the image
            img = Image.open(image_path)
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize if too large (max 1024x1024 to reduce processing time)
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            # Generate content with timeout
            response = self.model.generate_content([prompt, img], request_options={"timeout": 120})
            return response.text
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None


# --- Example Usage (Requires an image file path) ---
if __name__ == "__main__":
    # Create a dummy image file for demonstration purposes if it doesn't exist
    DUMMY_IMAGE_PATH = "dummy_road_sign.jpg"
    try:
        from PIL import Image, ImageDraw, ImageFont
        try:
            # Simple check to see if an image exists or needs to be generated
            if not Path(DUMMY_IMAGE_PATH).exists():
                print(f"Generating dummy image: {DUMMY_IMAGE_PATH}")
                img = Image.new('RGB', (400, 400), color = 'yellow')
                d = ImageDraw.Draw(img)
                # Draw a simple warning triangle (common cautionary sign shape)
                d.polygon([(200, 50), (50, 350), (350, 350)], outline='red', width=10)
                d.text((150, 200), "DANGER", fill=(0, 0, 0), font_size=40)
                img.save(DUMMY_IMAGE_PATH)
        except ImportError:
             print("Pillow not installed. Cannot generate dummy image. Please manually create a dummy_road_sign.jpg.")
             if not Path(DUMMY_IMAGE_PATH).exists():
                 print("Exiting example as image is missing.")
                 exit()
    except ImportError:
        # If Pillow is not available, proceed only if the file exists
        if not Path(DUMMY_IMAGE_PATH).exists():
             print("Pillow is not installed and required for dummy image generation. Please install it with 'pip install Pillow' or provide an image.")
             exit()
    
    # 1. Initialize the handler
    try:
        handler = MultimodalHandler()

        # 2. Define the analysis prompt
        analysis_prompt = (
            "Analyze this image in the context of Indian road safety codes (IRC). "
            "Identify the type of road sign and describe its meaning, paying attention "
            "to shape and color contrast. If it's an accident scene, assess potential factors."
        )

        print(f"\n--- Analyzing Image: {DUMMY_IMAGE_PATH} ---")
        
        # 3. Perform the analysis
        result = handler.analyze_image(DUMMY_IMAGE_PATH, analysis_prompt)

        # 4. Print the result
        if result:
            print("\n--- Model Analysis ---")
            print(result)
            print("----------------------")
        else:
            print("\nAnalysis failed.")
            
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
