from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
import time

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"{request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")
            
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        logger.info(f"{request.method} {request.url.path} took {process_time:.3f}s")

        return response