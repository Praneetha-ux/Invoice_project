import json

def validate_invoice_data(invoice_data):
    """
    Validate the given invoice data based on specific rules:
    1. Invoice Number should start with 'INV-'
    2. BSB should be '4321 432'
    3. Bank should be 'ANZ Bank'
    4. Total Due should be more than $1000
    """
    # Validation logic
    validation_results = {
        "invoice_number": invoice_data.get("invoice_number", "").startswith("INV-"),
        "bsb": invoice_data.get("payment_info", {}).get("bsb", "").strip() == "4321 432",
        "bank": invoice_data.get("payment_info", {}).get("bank", "").strip() == "ANZ Bank",
        "total_due": float(invoice_data.get("total_due", "0").replace(",", "")) < 1000
    }

    # Check if all validations passed
    all_valid = all(validation_results.values())

    return {
        "all_valid": all_valid,
        "details": validation_results
    }

# Simulating the input as provided JSON data
invoice_data = {
    "invoice_number": "INV-3337",
    "from": {
        "company": "DEMO - Sliced Invoices",
        "order_number": "12345",
        "suite": "5A-1204",
        "street": "123 Somewhere Street",
        "city": "Your City",
        "state": "AZ",
        "zip": "12345",
        "email": "admin@slicedinvoices.com"
    },
    "to": {
        "company": "Test Business",
        "street": "123 Somewhere St",
        "city": "Melbourne",
        "state": "VIC",
        "zip": "3000",
        "email": "test@test.com"
    },
    "invoice_date": "January 25, 2016",
    "due_date": "January 31, 2016",
    "total_due": "900.00",
    "services": [
        {
            "service": "Web Design",
            "rate": "20000.00",
            "price": "20000.00",
            "adjustment": "0.00%",
            "subtotal": "20000.00"
        }
    ],
    "tax": "2000.00",
    "total": "22000.00",
    "payment_info": {
        "bank": "ANZ Bank",
        "account_number": "1234 1234",
        "bsb": "4321 432"
    },
    "payment_terms": "Payment is due within 30 days from date of invoice. Late payment is subject to fees of 5% per month."
}

# Perform validation
validation_result = validate_invoice_data(invoice_data)

# Output the validation result
print("Validation Summary:")
print(f"All Fields Valid: {'Yes' if validation_result['all_valid'] else 'No'}")
for field, is_valid in validation_result["details"].items():
    print(f"{field}: {'Valid' if is_valid else 'Invalid'}")
