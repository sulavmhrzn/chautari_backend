import time
from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView

from utils.envelope import Envelope


class PingView(APIView):
    def get(self, request):
        start_time = time.time()

        ping_data = {
            "ping": "pong",
            "timestamp": datetime.now().isoformat(),
            "version": getattr(settings, "API_VERSION", "1.0.0"),
            "environment": getattr(settings, "ENVIRONMENT", "development"),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "status": "healthy",
            "uptime": "Available",
        }

        return Envelope.success_response(ping_data, status_code=status.HTTP_200_OK)
