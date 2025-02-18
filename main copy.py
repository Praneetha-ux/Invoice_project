import os
from dotenv import load_dotenv
import replicate

# Load API token from .env file
load_dotenv()  # Load environment variables from the .env file
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    raise ValueError("Replicate API token not found. Please set it in the .env file.")

# Initialize the Replicate client
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Define the input log files to be processed
input_files = ["input_log.txt","input2_log.txt", "input3_log.txt", "input4_log.txt", "input5_log.txt"]

# Read the input logs from the text files
def read_input_log(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist. Please create it with the input log.")

# Define the task for masking PII
def process_log(input_log):
    prompt = f"""
    Task: Mask all personally identifiable information (PII) such as names, 
    phone numbers, and email addresses in the following conversation log.
    - Replace all occurrences of first and last names with "***". 
      If the names are in a recognizable format (e.g., "John Doe" or "Jane Smith"), replace both parts with "***".
    - For any phone numbers present in the chat, replace them with the format "XXXX". 
      If multiple phone numbers appear, ensure to mask them similarly with the placeholder "XXXX".
    - Replace email addresses with "###".
    - Review the conversation carefully for other forms of PII, such as home addresses or company names, and mask them if identified.
    
    Expected Output: 
    A masked version of the conversation log with all personally identifiable information removed as per the above guidelines.
    
    Conversation log:
    {input_log}
    """
    
    try:
        response = replicate.run(
            "meta/meta-llama-3-8b-instruct",
            input={"prompt": prompt}
        )
        
        # Clean and format the response
        def format_response(raw_response):
            if isinstance(raw_response, list):
                return "\n".join(raw_response)
            elif isinstance(raw_response, dict):
                return raw_response.get("output", "No output found")
            else:
                return str(raw_response)
        
        masked_output = format_response(response)
        
        # Add final formatting
        formatted_output = f"""
        === Masked Conversation Log ===
        {masked_output.strip()}

        === Masked Information Summary ===
        """
        return formatted_output
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Process each input file and save the output
for index, input_file in enumerate(input_files, start=1):
    input_log = read_input_log(input_file)
    processed_output = process_log(input_log)
    
    # Define output file name
    output_file_name = f"output{index}_log.txt"
    
    # Write the processed output to the corresponding output file
    with open(output_file_name, "w") as output_file:
        output_file.write(processed_output)

    print(f"Processed {input_file} and saved the output to {output_file_name}")
