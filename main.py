import replicate
import pdfplumber
import json, re


# Set your Replicate API token
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


# Initialize Replicate client
replicate.Client(api_token=REPLICATE_API_TOKEN)

def extract_text_from_pdf(pdf_file_path):
    """
    Extract text content from a PDF file using pdfplumber.
    """
    with pdfplumber.open(pdf_file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def validate_invoice_data(invoice_data):
    """
    Validate the extracted invoice data against the given conditions.
    """
       # Validation logic
    # validation_results = {
    #     "invoice_number": invoice_data.get("invoice_number", "").startswith("INV-"),
    #     "bsb": invoice_data.get("payment_info", {}).get("bsb", "").strip() == "4321 432",
    #     "bank": invoice_data.get("payment_info", {}).get("bank", "").strip() == "ANZ Bank",
    #     "total_due": float(invoice_data.get("total_due", "0").replace(",", "")) < 1000
    # }
    # return validation_results

    validation_results={}
    invoice_num=invoice_data["invoice_number"]
    if(invoice_num.startswith("INV-")):
        validation_results["invoice_num"]=True
    else:
        validation_results=False
    invoice_bsb=invoice_data["bank_info"]["bsb"]
    if(invoice_bsb=="4321 432"):
        validation_results["invoice_bsb"]=True
    else:
        validation_results=False 
    invoice_bank=invoice_data["bank_info"]["bank_name"]
    if(invoice_bank=="ANZ Bank"):
        validation_results["invoice_bank"]=True
    else:
        validation_results=False
    invoice_due=invoice_data["total_due"]
    if(invoice_due<"1000"):
        validation_results["invoice_due"]=True
    else:
        validation_results["invoice_due"]=False

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
        Use only specific keys like in the output for validation  and when json is saved in the local the keys should be same
        invoice_number should be invoice_number,total_due should be total_due only,bsb should be bsb only,total_due should be total_due only.
        The json which we got should have got should have the all same keys which I have mentioned above. They shouldn't be different from one another.
        The keywords should not change they should be constant
        for example:invoice_number should be invoice_number:,bsb bank should be bsb only: only,bank_name should be bank_name only 
        total_due should be total_due only.
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
    pdf_file_path = 'invoice_3.pdf'  # Replace with dynamic input if needed
    file_name = pdf_file_path.split('.')[0]
    try:
        # Extract text content from the PDF
        print("Extracting text from the PDF...")
        pdf_text = extract_text_from_pdf(pdf_file_path)

        # Process the text with the LLaMA model
        print("Processing invoice with AI model...")
        structured_data = process_invoice_with_model(pdf_text)

        print("Extracted Invoice Data:")
        # print(json.dumps(structured_data, indent=4))
        with open(f"{file_name}.json", "w") as file:
            json.dump(structured_data, file, indent=4)


        # Validate the extracted invoice data
        print("Validating the extracted invoice data...")
        validation_results = validate_invoice_data(structured_data)

        print("Validation Summary:")
        for field, is_valid in validation_results.items():
            print(f"{field}: {'Valid' if is_valid else 'Invalid'}")

    except Exception as e:
        print(f"Error processing the invoice: {e}")

if __name__ == "__main__":
    main()


