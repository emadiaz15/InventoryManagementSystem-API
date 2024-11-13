def format_date(date):
    return date.strftime('%Y-%m-%d')

def generate_unique_code():
    import uuid
    return str(uuid.uuid4())
