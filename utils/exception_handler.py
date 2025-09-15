from rest_framework.views import exception_handler

from utils.envelope import Envelope


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return Envelope.error_response(
            error=response.data, status_code=response.status_code
        )
    return response
