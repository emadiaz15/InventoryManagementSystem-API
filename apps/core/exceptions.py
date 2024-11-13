class CustomAPIException(Exception):
    status_code = 400
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
