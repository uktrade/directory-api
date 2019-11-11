from requests import Response


def create_response(json_body={}, status_code=200, content=None):
    response = Response()
    response.status_code = status_code
    response.json = lambda: json_body
    response._content = content
    return response
