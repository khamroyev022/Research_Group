import time
import logging

api_logger = logging.getLogger("api")

class APILogMiddleware:
    LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in self.LOG_METHODS:
            return self.get_response(request)

        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else "Anonymous"
        ip = request.META.get("REMOTE_ADDR")
        lang = request.headers.get("Accept-Language", "")

        api_logger.info(
            f'{request.method} {request.get_full_path()} | '
            f'Status={response.status_code} | User={user} | IP={ip} | Lang={lang} | {duration:.2f}s'
        )
        return response
