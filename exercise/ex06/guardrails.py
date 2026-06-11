from ex03.filter import detect_intents

ALLOW_RULES = {
    'data_request': lambda all_intents: all(intent in all_intents for intent in ('data_request',)),
    'send_email': lambda all_intents: all(intent in all_intents for intent in ('send_email', 'data_request')),
}

def action_guardrails(messages):
    all_intents = []
    for message in messages:
        intents = detect_intents(message.get('content'))
        all_intents.extend(intents)
    current_intent = all_intents[-1] if all_intents else None
    if current_intent in ALLOW_RULES:
        rule = ALLOW_RULES.get(current_intent)
        if not rule(all_intents):
            # rule says no
            # -- this is relatively weak - can you see why? 
            # -- how to make it stronger?
            error = f'{current_intent=} rule denies {all_intents=}. Stop all activity immediately.'
            messages[-1].update({
                'role': 'user',
                'content': error})
    return messages


def sanitize(text):
    # we only sanitize input, output
    # -- action checks are now done in action_guardrails
    intents = detect_intents(text)
    redacted_text, found = redact_pii(text)
    return redacted_text