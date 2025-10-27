import json
import time

from v2.models import RequestLog

from fastapi import Request, Response

from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


def save_log(data: dict) -> None:
    RequestLog.create(**data)


class StatisticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith(("/dashboard", "/docs", "/openapi.json")):
            return await call_next(request)

        start_time = time.time()
        body_bytes = await request.body()

        async def receive():
            return {"type": "http.request", "body": body_bytes}

        scoped_request = Request(request.scope, receive)
        response, status_code, error_message = None, 500, None

        try:
            response = await call_next(scoped_request)
            status_code = response.status_code
        except Exception as error:
            error_message = str(error)
            response = Response("Internal Server Error", status_code=500)

        latency_ms = int((time.time() - start_time) * 1000)

        log_data = {
            "client_id": request.headers.get("client-id"),
            "method": request.method,
            "path": request.url.path,
            "params": json.dumps(dict(request.query_params)),
            "status_code": status_code,
            "latency_ms": latency_ms,
            "client_host": request.client.host or "unknown",
            "headers": json.dumps(dict(request.headers)),
            "body": body_bytes.decode("utf-8", "ignore"),
            "error_message": error_message,
        }

        await run_in_threadpool(
            save_log, log_data
        )

        return response
