import os
import json
from openai import OpenAI
import schemas

FEATHERLESS_API_KEY = os.environ.get("FEATHERLESS_API_KEY", "mock-key")
FEATHERLESS_BASE_URL = os.environ.get("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
# PINNED: Standard instruct model only. Do NOT swap to community/uncensored fine-tunes.
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

client = OpenAI(
    base_url=FEATHERLESS_BASE_URL,
    api_key=FEATHERLESS_API_KEY
)

def extract_candidates_from_search(query: str, search_results: list) -> dict:
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "candidates": [
                {"name": f"{query} Pvt Ltd", "country": "India", "confidence": 0.85, "sources": 5}
            ],
            "reliable_sources": 5,
            "negative_news_found": False,
            "overall_confidence": "medium"
        }
        
    prompt = f"""
    You are an AI investigator. Analyze the following search results for the entity "{query}".
    Extract possible matching companies. Return JSON strictly following this schema:
    {{
        "candidates": [
            {{"name": "Company Name", "country": "Country Name", "confidence": 0.0 to 1.0 (float), "sources": integer}}
        ],
        "reliable_sources": integer,
        "negative_news_found": boolean,
        "overall_confidence": "high" or "medium" or "low"
    }}
    Search results: {json.dumps(search_results)}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return {
            "candidates": [],
            "reliable_sources": 0,
            "negative_news_found": False,
            "overall_confidence": "low"
        }

def extract_document_fields(ocr_text: str) -> dict:
    """Uses LLM to extract structured JSON from raw OCR text."""
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "invoice_date": {"value": "2026-07-03", "confidence": 0.95, "status": "extracted"},
            "amount": {"value": "3200", "confidence": 0.98, "status": "extracted"}
        }
    prompt = f"""
    You are an expert data extractor. Extract key fields from the following OCR text.
    Return JSON containing a 'fields' object where keys are field names (e.g., 'invoice_date', 'amount', 'tax_id')
    and values are objects with 'value' (string), 'confidence' (0.0 to 1.0), and 'status' (must be one of "extracted", "low_confidence", "not_found").
    
    OCR Text:
    {ocr_text}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content).get("fields", {})
    except Exception as e:
        print(f"LLM field extraction failed: {e}")
        return {}

def summarize_case(validation: dict, evidence: dict) -> dict:
    """Generates case summary and recommendation from Validation and Evidence."""
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "summary": "Invoice and contract amounts match. There is a flag regarding the date consistency.",
            "recommendation": "additional_documents_required"
        }
    prompt = f"""
    You are an AI investigator. Summarize the case based on the validation results and evidence below.
    CRITICAL: Never use the words "approved" or "rejected". Your output recommendation MUST BE EXACTLY ONE OF:
    "ready_for_manual_approval", "additional_documents_required", "further_investigation_recommended".
    Do not perform your own validation. Only summarize the provided validation results.
    
    Validation: {json.dumps(validation)}
    Evidence: {json.dumps(evidence)}
    
    Return JSON with 'summary' (string) and 'recommendation' (exact string).
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM summarize failed: {e}")
        return {"summary": "Error generating summary.", "recommendation": "further_investigation_recommended"}

def draft_followup(validation: dict) -> dict:
    """Drafts a follow-up message based on missing fields or flags."""
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "trigger_reason": "additional_documents_required",
            "drafted_message": "Hi, we are reviewing your invoice. Please provide the missing fields."
        }
    prompt = f"""
    Draft a polite follow-up message to the vendor regarding this case.
    Address the specific missing fields or flags from the validation data. Do NOT use generic boilerplate.
    
    Validation: {json.dumps(validation)}
    
    Return JSON with 'trigger_reason' (string) and 'drafted_message' (string).
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM drafting failed: {e}")
        return {"trigger_reason": "error", "drafted_message": "Please review the case manually."}

def reconstruct_field(field_name: str, context_text: str) -> dict:
    """Reconstructs a missing or low-confidence field."""
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "suggested_value": "Suggested Value",
            "confidence": "low"
        }
    prompt = f"""
    Suggest a possible value for the field '{field_name}' based on the following context text.
    Return JSON with 'suggested_value' (string) and 'confidence' ("low" or "medium").
    Context: {context_text}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM reconstruction failed: {e}")
        return {"suggested_value": "Unknown", "confidence": "low"}

def synthesize_case(documents_content: list) -> dict:
    """Synthesizes a cross-document narrative."""
    if FEATHERLESS_API_KEY == "mock-key":
        return {
            "narrative": "The invoice references Contract #4521, which specifies net-30 payment terms."
        }
    prompt = f"""
    Synthesize the following documents into a single coherent narrative for the investigation case.
    Documents: {json.dumps(documents_content)}
    Return JSON with 'narrative' (string).
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM synthesize failed: {e}")
        return {"narrative": "Error generating cross-document synthesis."}

