from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Network Copilot API", 
    description="API for network metrics and alerts",
    version="0.1.0"
)

# Pydantic models for response
class NetworkMetric(BaseModel):
    ts: datetime.datetime
    host: str
    latency: Optional[float] = None
    error_rate: Optional[float] = None
    traffic: Optional[float] = None
    is_anomaly: bool

class MetricsResponse(BaseModel):
    metrics: List[NetworkMetric]

class Alert(BaseModel):
    ts: datetime.datetime
    host: str
    reason: str

class AlertsResponse(BaseModel):
    alerts: List[Alert]

@app.get("/metrics/latest", response_model=MetricsResponse)
async def get_latest_metrics():
    """Get latest network metrics"""
    logger.info("Fetching latest network metrics")
    # Return empty list - no final logic yet (to be implemented with data pipeline)
    return {"metrics": []}

@app.get("/alerts", response_model=AlertsResponse)
async def get_alerts():
    """Get active alerts"""
    logger.info("Fetching active alerts")
    # Return empty list - no final logic yet (to be implemented with detection module)
    return {"alerts": []}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")
