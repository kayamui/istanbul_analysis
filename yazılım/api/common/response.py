# api/common/response.py
def http_response_object(success: bool, message: str, data: dict, code: int):
    return {
        "success": success,
        "message": message,
        "data": data
    }, code