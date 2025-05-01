from pydantic import BaseModel
from typing import Optional

# -----------------------------------------------
# Model: Structured output for extracted metadata
# -----------------------------------------------
class ExtractedData(BaseModel):
    invoice_number: Optional[str]   # e.g. "INV-1023"
    company_name: Optional[str]     # e.g. "Acme Corp"
    due_date: Optional[str]         # e.g. "2025-06-30"
    amount: Optional[str]           # e.g. "$5,000"
    signatories: Optional[str]      # e.g. "John Doe, CFO"
    summary: Optional[str]          # e.g. "Invoice for Q2 marketing services"
