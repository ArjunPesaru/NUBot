import streamlit as st
import requests
from dotenv import load_dotenv
import os
import urllib.parse

# Load environment variables from .env file
load_dotenv('frontend.env', override=True)

# Get the backend API URL
API_URL = os.getenv('API_URL', 'http://localhost:5002')
endpoint = urllib.parse.urljoin(API_URL, "NuBot/")

# UI setup
st.title("NuBot Chat Interface")
st.markdown("### Ask NuBot any question!")

# User input
query = st.text_input("Enter your query:")

# Handle Submit button
if st.button("Submit"):
    if query:
        try:
            # Make POST request to backend
            response = requests.post(endpoint, json={"query": query})

            # Handle response
            if response.status_code == 200:
                st.success("Response from NuBot:")
                st.write(response.json())
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a query before submitting.")
