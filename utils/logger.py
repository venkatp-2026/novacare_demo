"""Request/Response logging middleware for debugging AI agent calls."""
import json
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("novacare_api")


class RequestResponseLogger(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for static files and health checks
        if request.url.path.startswith('/static') or request.url.path == '/healthz':
            return await call_next(request)

        # Generate request ID for tracking
        request_id = f"{int(time.time() * 1000)}"

        # Log request
        logger.info("=" * 80)
        logger.info(f"🔵 INCOMING REQUEST [{request_id}]")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.url.path}")
        logger.info(f"Query Params: {dict(request.query_params)}")
        logger.info(f"Headers: {dict(request.headers)}")

        # Log request body for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        body_json = json.loads(body.decode())
                        logger.info(f"Request Body: {json.dumps(body_json, indent=2)}")
                    except json.JSONDecodeError:
                        logger.info(f"Request Body (raw): {body.decode()[:500]}")

                    # Reconstruct request with body for downstream processing
                    async def receive():
                        return {"type": "http.request", "body": body}

                    request._receive = receive
            except Exception as e:
                logger.error(f"Error reading request body: {e}")

        # Process request and measure time
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(f"🟢 RESPONSE [{request_id}]")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Duration: {duration:.3f}s")

            # Try to log response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            try:
                response_json = json.loads(response_body.decode())
                logger.info(f"Response Body: {json.dumps(response_json, indent=2)}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.info(f"Response Body (raw): {response_body.decode('utf-8', errors='ignore')[:500]}")

            logger.info("=" * 80)

            # Return response with reconstructed body
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"🔴 ERROR [{request_id}]")
            logger.error(f"Duration: {duration:.3f}s")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 80)
            raise


def log_ai_agent_call(endpoint: str, input_data: dict, response_data: dict, success: bool = True):
    """
    Dedicated logging function for AI agent tool calls.
    Use this in your route handlers to explicitly log AI interactions.
    """
    logger.info("🤖 AI AGENT TOOL CALL")
    logger.info(f"Endpoint: {endpoint}")
    logger.info(f"Input: {json.dumps(input_data, indent=2, default=str)}")
    logger.info(f"Output: {json.dumps(response_data, indent=2, default=str)}")
    logger.info(f"Success: {'✅' if success else '❌'}")
    logger.info("-" * 80)
