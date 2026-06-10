from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
import re
import spacy

# setup
analyzer = AnalyzerEngine()       # lädt Standard-Recognizer (z.B. PHONE_NUMBER, EMAIL, ...)
anonymizer = AnonymizerEngine()   # für Masking / Redaction
nlp = spacy.load("en_core_web_sm")


def redact_pii(text):
    results = analyzer.analyze(text=text,
                               entities=["PHONE_NUMBER", "CREDIT_CARD"],
                               language='en')
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text, len(anonymized.items) > 0


def detect_intents(text):    
    intents = []
    doc = nlp(text.lower())
    if set(tok.lemma_ for tok in doc) >= {"retrieve", "datum"}:
        intents.append("data_request")
    if set(tok.lemma_ for tok in doc) >= {"send", "email"}:
        intents.append("send_email")
    if set(tok.lemma_ for tok in doc) >= {"job", "confirm"}:
        intents.append("confirm_job")
    if set(tok.lemma_ for tok in doc) >= {"summarize", "above"}:
        intents.append("leak_prompt")
    return intents


def sanitize(text):
    intents = detect_intents(text)
    redacted_text, found = redact_pii(text)
    if "confirm_job" in intents:
        raise ValueError("Unauthorized request to confirm a job application")
    if "leak_prompt" in intents:
        raise ValueError("Unauthorized request to leak the prompt")
    return redacted_text