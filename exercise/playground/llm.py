import os
import requests
from .util import read_env, load_yaml
from .tools import maybe_call_tools, tools_as_functions, list_tools

read_env()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "openai/gpt-oss-120b:free")
LLM_API_KEY = os.getenv("LLM_API_KEY")  # required
LLM_SYSTEM_PROMPT = os.getenv("LLM_SYSTEM_PROMPT", "playground/prompts/system.yaml")


def ask_llm(history, prompt, system_prompt=None, use_tools=True, timeout=90):
    """
    Call OpenRouter-compatible API using requests and return assistant text.
    - history: list of {"role": "user"|"assistant", "content": str}
    - prompt: current user prompt (str)
    """
    # Build messages: include prior history then the new user prompt
    messages = []
    for msg in history:
        # ensure only supported roles are passed
        role = msg.get("role", "user")
        if role not in ("user", "assistant", "system"):
            role = "user"
        messages.append({"role": role, "content": msg.get("content", "")})
    
    # if this is the first message, add the system prompt
    if not system_prompt:
        system_prompt = load_yaml(LLM_SYSTEM_PROMPT).get('prompt')
    if not messages or messages[0].get('role') != 'system':
        messages.insert(0, {"role": "system", "content": system_prompt})    
    # add current prompt
    messages.append({"role": "user", "content": prompt})
    
    # add tools, optional
    extra = {}
    if use_tools and len(list_tools()) > 0:
        extra.update({
            'tools': tools_as_functions(),
            'tools_choice': "auto",
        })

    # check intents
    from ex06.guardrails import action_guardrails
    action_guardrails(messages)
    
    # check guardrails, pii-filter
    from ex03.guardrails import input_guardrails, output_guardrails
    input_guardrails(messages)
    
    # call llm and tools
    extra.update(timeout=timeout)
    data = chat_completions(messages, **extra)
    data = maybe_call_tools(data, messages)
    
    # extract response
    # -- The exact response layout can vary; this handles standard chat-completions style
    # -- Try to extract the assistant content from choices[0].message.content
    try:
        message = data["choices"][0]["message"]
        assistant_text = message["content"]
    except Exception:
        # Fallback: join any text fields present
        assistant_text = ""
        if "choices" in data:
            for choice in data["choices"]:
                msg = choice.get("message", {}) or choice.get("delta", {})
                content = msg.get("content") or msg.get("text")
                if content:
                    assistant_text += content

    # ex03
    output_guardrails(assistant_text)

    # ex05
    from ex05.auditlog import generate_auditlog
    generate_auditlog(messages, data["choices"])
    return assistant_text


def chat_completions(messages, timeout=90, **extra):
    # damit können wir den call zum LLM für Testzwecke ersetzen (z.B. mit einem MagicMock)
    if not LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY environment variable not set")

    url = f"{LLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL_ID,
        "messages": messages,
        # you can tune temperature, max_tokens, etc. here
        "temperature": 0.0,
        "max_tokens": 1024 * 2,
        "reasoning": {
            "enabled": True,
            "effort": "minimal",
        }
    }
    payload.update(extra)
    resp = requests.post(url, 
                         headers=headers, 
                         json=payload, 
                         timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data

