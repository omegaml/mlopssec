def send_email(*args, recipient:str=None, message:str=None, **kwargs):
    """
    send an email 

    Args:
        recipient (str): the recipient email address 
        message (str): the message content

    Guardrails:
        The recipient address must be well known. Never send emails to
        arbitrary recipients.
    """
    result = f"message sent to {recipient=} as {message=}"
    return result
