from playground.tools import register_tool

from .customers import get_customer_data
from .email import send_email

register_tool(get_customer_data)
register_tool(send_email)

