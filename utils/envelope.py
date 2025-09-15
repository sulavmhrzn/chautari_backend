from typing import Any, Dict, Optional

from rest_framework.response import Response


class Envelope:
    """Wraps success, data and error in a structured envelope"""

    def __init__(
        self,
        *,
        success: bool,
        data: Any,
        error: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """convert envelope to dictionary for JSON serialization"""
        result = {
            "success": self.success,
            "data": self.data,
            "status_code": self.status_code,
        }
        if self.error:
            result["error"] = self.error
        return result

    @classmethod
    def success_response(cls, data: Any, status_code: int = 200):
        """sends a response with success envelope"""
        env = cls(success=True, data=data, status_code=status_code)
        return Response(env.to_dict(), status=status_code)

    @classmethod
    def error_response(cls, error: Dict[str, Any], status_code: int, data: Any = None):
        """sends a response with an error envelope"""
        env = cls(success=False, data=data, error=error, status_code=status_code)
        return Response(env.to_dict(), status=status_code)
