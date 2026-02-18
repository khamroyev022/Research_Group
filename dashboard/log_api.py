import re
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .pagination import DefaultPagination

LOG_FILE = Path("logs/api.log")

LOG_PATTERN = re.compile(
    r"(?P<level>\w+)\s+"
    r"(?P<datetime>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+"
    r"api\s+\|\s+"
    r"(?P<method>\w+)\s+(?P<url>\S+)\s+\|\s+"
    r"Status=(?P<status>\d+)\s+\|\s+"
    r"User=(?P<user>\S+)\s+\|\s+"
    r"IP=(?P<ip>\S+)\s+\|\s+"
)

def parse_logs():
    if not LOG_FILE.exists():
        return []

    logs = []
    current_lines = []

    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if re.match(r"(INFO|ERROR|WARNING|DEBUG)\s+\d{4}", line):
                if current_lines:
                    full_line = " ".join(current_lines)
                    match = LOG_PATTERN.search(full_line)
                    if match:
                        logs.append(match.groupdict())
                current_lines = [line.strip()]
            else:
                current_lines.append(line.strip())
        if current_lines:
            full_line = " ".join(current_lines)
            match = LOG_PATTERN.search(full_line)
            if match:
                logs.append(match.groupdict())

    return logs


class LogListAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    def get(self, request):
        logs = parse_logs()
        level = request.query_params.get("level")
        method = request.query_params.get("method")
        status = request.query_params.get("status")
        user = request.query_params.get("user")
        date = request.query_params.get("date")
        if level:
            logs = [l for l in logs if l["level"].upper() == level.upper()]
        if method:
            logs = [l for l in logs if l["method"].upper() == method.upper()]
        if status:
            logs = [l for l in logs if l["status"] == status]
        if user:
            logs = [l for l in logs if l["user"].lower() == user.lower()]
        if date:
            logs = [l for l in logs if l["datetime"].startswith(date)]
        paginator = DefaultPagination()
        paginated = paginator.paginate_queryset(logs, request)

        return paginator.get_paginated_response({
            "count": len(logs),
            "data": paginated
        })
