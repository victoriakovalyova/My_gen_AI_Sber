from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

log = logging.getLogger(__name__)

class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования доступа к API.
    Перехватывает входящие HTTP-запрос, а затем логирует.
    """
    async def dispatch(self, request, call_next):
        """Обрабатывает входящий запрос."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        log.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
        return response

def add_access_log_middleware(app: FastAPI):
    """Функция для добавления AccessLogMiddleware в FastAPI."""
    app.add_middleware(AccessLogMiddleware)