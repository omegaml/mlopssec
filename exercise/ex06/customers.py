def get_customer_data(*args, customer_id:str ='', **kwargs):
    """
    a tool to get customer data

    Args:
        customer_id (str): the customer id
    """
    data = {
        '0001': {
            'name': 'Charles Taylor',
            'location': 'New York',
            'email': 'charles.taylor@greatcompany.com',
        },

        '0002': {
            'name': 'Bugs Bunny',
            'location': 'Disney Land',
            'email': 'bugs.bunny@disneyland.com',
        }
    }
    return data.get(customer_id) or 'no data found'

