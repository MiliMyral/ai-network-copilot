from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime
import logging
import sys
import os

# Add the api directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Network Copilot API",
    description="API for network metrics and alerts",
    version="0.1.0"
)

# Import database utility
from database import get_latest_metrics as db_get_latest_metrics, get_alerts as db_get_alerts, get_hosts as db_get_hosts

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

class HostsResponse(BaseModel):
    hosts: List[str]

@app.get("/metrics/latest", response_model=MetricsResponse)
async def get_latest_metrics_endpoint(limit: int = 100):
    """Get latest network metrics"""
    logger.info(f"Fetching latest {limit} network metrics")
    try:
        metrics = db_get_latest_metrics(limit)
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/alerts", response_model=AlertsResponse)
async def get_alerts_endpoint(limit: int = 50):
    """Get active alerts"""
    logger.info(f"Fetching latest {limit} alerts")
    try:
        alerts = db_get_alerts(limit)
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@app.get("/hosts", response_model=HostsResponse)
async def get_hosts_endpoint():
    """Get list of unique hosts"""
    logger.info("Fetching unique hosts")
    try:
        hosts = db_get_hosts()
        return {"hosts": hosts}
    except Exception as e:
        logger.error(f"Error fetching hosts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch hosts")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")
