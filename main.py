"""
main.py: The entry point for the RoadSafetyGPT application.
It imports and runs the Streamlit app defined in app.py.
"""
import streamlit.web.cli as stcli
import sys
import os

# Add the parent directory to the path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", "app/app.py"]
    sys.exit(stcli.main())
