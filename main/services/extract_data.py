import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict

# ------------------------------------------------------------
# ✅ Client Setup: Initialize Azure Form Recognizer
# ------------------------------------------------------------
def get_form_recognizer_client() -> DocumentAnalysisClient:
    """
    Creates and returns a Form Recognizer client using credentials 
    from environment variables.

    Raises:
        ValueError: If endpoint or key is missing in the environment.

    Returns:
        DocumentAnalysisClient: Authenticated client instance.
    """
    endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

    if not endpoint or not key:
        raise ValueError("AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY must be set.")

    return DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# ------------------------------------------------------------
# ✅ Extraction Logic: Uses Azure’s prebuilt-invoice model
# ------------------------------------------------------------
def extract_from_pdf(file_path: str) -> Dict[str, str]:
    """
    Extracts key invoice fields from a PDF using the Azure 
    Form Recognizer's prebuilt-invoice model.

    Args:
        file_path (str): Absolute or relative path to the PDF file.

    Returns:
        Dict[str, str]: Extracted fields: invoice number, company, due date, amount, and signatories.
    """
    client = get_form_recognizer_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-invoice", f)
        result = poller.result()

    # Define expected output schema
    extracted = {
        "invoice_number": None,
        "company_name": None,
        "due_date": None,
        "amount": None,
        "signatories": None,
    }

    # Defensive check to avoid index errors
    if result.documents:
        document = result.documents[0]
        for field_name, field in document.fields.items():
            if field_name == "InvoiceId":
                extracted["invoice_number"] = field.value
            elif field_name == "VendorName":
                extracted["company_name"] = field.value
            elif field_name == "DueDate":
                extracted["due_date"] = str(field.value) if field.value else None
            elif field_name == "AmountDue":
                extracted["amount"] = str(field.value) if field.value else None
            elif field_name == "CustomerName":
                extracted["signatories"] = field.value

    return extracted
