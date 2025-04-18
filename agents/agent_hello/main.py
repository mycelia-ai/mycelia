from fastapi import FastAPI
from pydantic import BaseModel
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_hello")

# Define Prometheus metrics
REQUEST_COUNT = Counter("hello_request_count", "Count of hello requests received")

class Message(BaseModel):
    data: dict

@app.post("/hello.request")
async def handle_request(message: Message):
    """Handle incoming messages on the `hello.request` topic."""
    REQUEST_COUNT.inc()  # Increment the counter for each request
    logger.info(f"Received message on 'hello.request': {message.data}")
    response = {"response": "Hello, world!"}
    logger.info(f"Responding on 'hello.response': {response}")
    return response

@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
