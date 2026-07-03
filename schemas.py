from pydantic import BaseModel
from typing import List, Optional, Dict, Literal

# --- Evidence Schema ---
class EvidenceCandidate(BaseModel):
    name: str
    country: str
    confidence: float
    sources: int

class Evidence(BaseModel):
    query: str
    candidates: List[EvidenceCandidate]
    selected_candidate: Optional[str] = None
    sources_searched: int
    reliable_sources: int
    negative_news_found: bool
    overall_confidence: str

# --- Summary Output ---
class SummaryOutput(BaseModel):
    case_id: str
    summary: str
    recommendation: Literal["ready_for_manual_approval", "additional_documents_required", "further_investigation_recommended"]

# --- Follow-up Draft Output ---
class FollowupDraftOutput(BaseModel):
    case_id: str
    trigger_reason: str
    drafted_message: str

# --- Reconstruction Output ---
class ReconstructionOutput(BaseModel):
    document_id: str
    field_name: str
    suggested_value: str
    basis: str
    confidence: str

# --- Synthesis Output ---
class SynthesisOutput(BaseModel):
    case_id: str
    documents_included: List[str]
    narrative: str

# --- Input Schemas (Consumed but not owned) ---
class FieldData(BaseModel):
    value: str
    confidence: float
    status: Literal["extracted", "low_confidence", "not_found"]

class ExtractionSchema(BaseModel):
    document_id: str
    document_type: str
    fields: Dict[str, FieldData]

class ValidationSchema(BaseModel):
    case_id: str
    amount_match: bool
    currency_match: bool
    date_consistent: bool
    vendor_match: bool
    purpose_code_plausible: bool
    purpose_code_note: str
    missing_fields: List[str]
    flags: List[str]

# --- API Request Schemas ---
class UploadRequest(BaseModel):
    filename: str

class ExtractRequest(BaseModel):
    document_id: str
    ocr_text: str

class ValidateRequest(BaseModel):
    case_id: str
    extraction: ExtractionSchema

class EvidenceRequest(BaseModel):
    case_id: str
    query: str

class SummarizeRequest(BaseModel):
    case_id: str
    validation: ValidationSchema
    evidence: Evidence

class FollowupDraftRequest(BaseModel):
    case_id: str
    validation: ValidationSchema

class ReconstructRequest(BaseModel):
    document_id: str
    field_name: str
    context_text: str

class SynthesizeRequest(BaseModel):
    case_id: str
    documents: List[str]
