import streamlit as st
import replicate
import pdfplumber
import json
import re

# Set your Replicate API token

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


# Initialize Replicate client
replicate.Client(api_token=REPLICATE_API_TOKEN)

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file using pdfplumber.
    """
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def validate_invoice_data(invoice_data):
    """
    Validate the extracted invoice data against the given conditions.
    """
    # Get the fields, ensure they're strings, and apply validation
    invoice_number = str(invoice_data.get("invoiceNumber", ""))
    bsb = str(invoice_data.get("paymentDetails", {}).get("bsbNumber", ""))
    bank = str(invoice_data.get("paymentDetails", {}).get("bank", ""))
    total = str(invoice_data.get("total", ""))

    # Validation conditions
    validation_results = {
        "invoice_number": invoice_number.startswith("INV-"),
        "bsb": bsb.strip() == "4321 432",
        "bank": bank.strip() == "ANZ Bank",
        "total_due": total.strip() < "$1000",
    }

    return validation_results

def process_invoice_with_model(file_content):
    """
    Process the invoice text content with the LLaMA model through the Replicate API.
    """
    # Define the prompt for the model
    prompt = f"""
        You are a highly intelligent assistant. Parse the following raw invoice text into a structured JSON dictionary.

        Input:
        {file_content}

        ###Output format:
        valid JSON only. Do not include any other text other than valid JSON.
        """

    # Use Replicate to process the prompt
    response = replicate.run(
        "meta/meta-llama-3-8b-instruct",
        input={"prompt": prompt}
    )
    
    # Combine and parse the response
    combined_response = ''.join(response).strip()

    # Regular expression pattern to match JSON enclosed in backticks (```).
    json_pattern = r'```\n?({.*?})\n?```'

    # Extract JSON from the string
    json_match = re.search(json_pattern, combined_response, re.DOTALL)

    if json_match:
        json_str = json_match.group(1)  # Extract only the JSON part
    
    # Parse the JSON response into a Python dictionary
    dict_response = json.loads(json_str)

    return dict_response

def main():
    st.title("Invoice Processor Chatbot")
    st.write("Upload your invoice PDF, and the chatbot will convert it into a structured JSON dictionary.")

    uploaded_file = st.file_uploader("Upload Invoice (PDF)", type=["pdf"])

    if uploaded_file:
        # Extract text content from the PDF
        with st.spinner("Extracting text from the PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)

        # Process the text with the LLaMA model
        with st.spinner("Processing invoice with AI model..."):
            try:
                structured_data = process_invoice_with_model(pdf_text)
                st.subheader("Extracted Invoice Data:")
                st.json(structured_data)

                # Validate the extracted invoice data
                validation_results = validate_invoice_data(structured_data)

                st.subheader("Validation Summary:")
                for field, is_valid in validation_results.items():
                    st.write(f"{field}: {'Valid' if is_valid else 'Invalid'}")

            except Exception as e:
                st.error(f"Error processing the invoice: {e}")

if __name__ == "__main__":
    main()


