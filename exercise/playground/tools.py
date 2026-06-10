import json

# Simple tool registry
_tools = {}

def register_tool(func, name: str = "", description: str = ""):
    """
    Register a tool function callable by name.
    - name: unique tool name (str)
    - func: callable that accepts a single dict argument (parameters) and returns serializable result
    - description: short description for the tool
    """
    name = name or getattr(func, '__name__', '')
    description = description or getattr(func, '__doc__', f'the {name} tool')
    assert callable(func), f"{func} must be callable"
    assert name, f"{func} does not have a __name__, specify name="
    _tools[name] = {"func": func, "description": description}


def list_tools(subset=None):
    """Return registered tools metadata."""
    subset = subset or _tools.keys()
    return { name: spec for name, spec in _tools.items() if name in subset }


def call_tool(name: str, params: dict, timeout: int = 30):
    """Invoke a registered tool and return a JSON-serializable result."""
    if name not in _tools:
        raise RuntimeError(f"Tool not registered: {name}")
    func = _tools[name]["func"]
    # Tools should handle their own errors; we catch exceptions and return them as structured error
    try:
        result = func(**params)
        # ensure result is serializable
        try:
            json.dumps(result)
        except Exception:
            # fallback to string representation
            result = {"result": str(result)}
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tools_as_functions(valid_tools=None):
    """
    Return a list of tool definitions suitable for OpenAI-style 'functions' parameter.
    Each tool: { "name": str, "description": str, "parameters": { "type":"object", "properties": {...} } }
    We provide minimal parameter schema (freeform object) since tools accept dicts.
    """
    tools_param = []
    for name, meta in list_tools(valid_tools).items():
        # https://developers.openai.com/api/docs/guides/function-calling
        tools_param.append({
            "type": "function",
            "function": {
                "name": name,
                "description": meta.get("description", "") or f"the {name} tool",
                # minimal flexible schema: allow arbitrary object
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                },
                "return_type": "object",
            },
            "strict": False,
        })
    return tools_param

        
def maybe_call_tools(response, messages, timeout=90):
    """
    Inspect an LLM response (the parsed JSON from chat_completions).
    If it requests a tool call, execute the tool, append tool output to messages and
    call chat_completions again returning the new response object.
    - response: dict (parsed JSON from chat_completions)
    - messages: list of messages (will be extended in-place with assistant/tool/system messages)
    - valid_tools: list of the tool names available, or None to mean all tools in registry
    - returns: new_response dict if a tool was called and chat_completions re-run; otherwise None.
    
    Detection supports two forms:
    1) Function call style: response['choices'][0]['message'].get('function_call') with 'name' and 'arguments' (string JSON).
    2) Inline JSON in assistant content containing {"tool_call": {"name": ..., "params": {...}}}
    """
    from .llm import chat_completions
    
    # extract first choice message
    try:
        choice = response["choices"][0]
        msg = choice.get("message", {}) or {}
    except Exception:
        return response

    # 1) function_call style (preferred)
    tool_calls = msg.get("tool_calls")
    tool_name = None    
    if tool_calls:
        # we only support 1 call at a time
        tool_params = {}
        func_call = tool_calls[0].get('function', {})
        tool_name = func_call.get("name")
        args_raw = func_call.get("arguments", "")
        if args_raw:
            try:
                # arguments may be a JSON string
                tool_params = json.loads(args_raw)
            except Exception:
                # fallback: treat as empty or simple string param
                tool_params = {"_raw": args_raw}

    # 2) fallback: assistant content contains tool_call JSON
    if not tool_calls:
        assistant_text = msg.get("content", "") or ""
        try:
            start = assistant_text.find("{")
            end = assistant_text.rfind("}") + 1
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(assistant_text[start:end])
                if isinstance(parsed, dict) and "tool_call" in parsed:
                    tc = parsed["tool_call"]
                    tool_name = tc.get("name")
                    tool_params = tc.get("params", {}) or {}
        except Exception:
            pass

    if not tool_name:
        return response

    # Execute tool
    tool_result = call_tool(tool_name, tool_params, timeout=timeout)

    # Append original assistant message to messages (so model sees it), then tool output as system/tool message
    # Use consistent roles: append assistant then system with tool_output JSON
    assistant_content = msg.get("content", "")
    messages.append({"role": "assistant", "content": assistant_content})

    tool_output = {"tool_name": tool_name, "tool_result": tool_result}
    messages.append({"role": "system", "content": json.dumps({"tool_output": tool_output})})

    # Call LLM again with updated messages
    data = chat_completions(messages, timeout=timeout)
    return data