from flask import Flask, request, jsonify
from flask_login import current_user
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import uuid

# Logger setup: rotierendes Datei-Log
handler = RotatingFileHandler("playground/audit.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_logger.addHandler(handler)
audit_logger.propagate = False


def audit_log(user: str,
              prompt: str,
              response: str,
              document_ids: list,
              tool_calls: list,
              incident: str = None,
              extra: dict = None) -> str:
    """
    Erstellt einen Audit-Eintrag als JSON-Zeile und schreibt ihn ins Audit-Log.
    Returns: generated audit_id
    Felder:
      - audit_id: eindeutige ID für den Eintrag
      - user: Benutzerkennung (string)
      - prompt: eingegebener Prompt/Text
      - response: Antwort des Modells
      - document_ids: Liste der angezeigten Dokument-IDs
      - tool_calls: Liste von Tool-Call-Objekten (z.B. {name, input, output})
      - timestamp: ISO-8601 UTC Zeitstempel
      - incident: kurze Beschreibung eines Vorfalls (optional)
      - extra: optionales freies Feld für Metadaten
    """
    audit_id = str(uuid.uuid4())
    entry = {
        "audit_id": audit_id,
        "user": user,
        "prompt": prompt,
        "response": response,
        "document_ids": document_ids or [],
        "tool_calls": tool_calls or [],
        "timestamp": datetime.utcnow().isoformat(),
        "incident": incident,
        "extra": extra or {}
    }
    # Schreibe als JSON-Zeile ins Log (maschinenlesbar für Rekonstruktion)
    audit_logger.info(json.dumps(entry, ensure_ascii=False))
    return audit_id


def generate_auditlog(messages: list, response: dict, extra: dict = None) -> str:
    """
    Erzeugt einen Audit-Eintrag aus:
      - messages: Liste von Nachricht-Objekten (z.B. [{"role": "user", "user": "alice", "content": "..."}, ...])
      - response: Antwort-Objekt mit Feldern wie "text", "used_documents", "tool_calls"
      - extra: optionales Dict mit Metadaten (z.B. {"client_ip": "..."} )
    Returns: audit_id
    """
    # Bestimme user
    user = current_user.id
    user_contents = []
    # Bestimme prompt (konkatenieren aller user messages, falls vorhanden)
    prompt = " ".join(user_contents) if user_contents else (messages[-1].get("content") if messages and isinstance(messages[0], dict) else "")
    tool_calls = response.get("tool_calls") if isinstance(response, dict) else []
    incident = response.get("incident") if isinstance(response, dict) else None
    document_ids = [] 
    extra = extra or {}
    audit_id = audit_log(
        user=user or "anonymous",
        prompt=prompt,
        response=response,
        document_ids=document_ids,
        tool_calls=tool_calls,
        incident=incident,
        extra=extra
    )
    return audit_id