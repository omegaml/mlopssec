# add this in llm.py 
#    from ex03.guardrails import input_guardrails, output_guardrails
#
#    def ask_llm():
#       ...
#       input_guardrails(messages)
#       ...
#       return output_guardrails(assistant_text)

from .filter import sanitize

def input_guardrails(messages):
    for message in messages:
        try:
            safe_content = sanitize(message.get('content', '') or message.get('text',''))
            message['content'] = safe_content
        except Exception as e:
            message['content'] = f"*** this message has been removed due to {e}"
    return messages
    
def output_guardrails(response):
    try:
        safe_content = sanitize(message.get('content', '') or message.get('text',''))
    except Exception as e:
        safe_content = f"*** this message has been removed due to {e}"
    return safe_content
    