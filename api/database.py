"""
Database utility functions for AI Network Copilot API
"""
import os
import sqlite3
import datetime
from typing import List, Optional
from pydantic import BaseModel


class NetworkMetric(BaseModel):
    ts: datetime.datetime
    host: str
    latency: Optional[float] = None
    error_rate: Optional[float] = None
    traffic: Optional[float] = None
    is_anomaly: bool

def get_latest_metrics(limit: int = 100) -> List[NetworkMetric]:
    """Get latest network metrics from database"""
    CHEMIN_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "network.db")
    conn = sqlite3.connect(CHEMIN_DB)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ts, host, latency, error_rate, traffic, is_anomaly
        FROM network_metrics
        ORDER BY ts DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    metrics = []
    for row in rows:
        metrics.append(NetworkMetric(
            ts=datetime.datetime.fromisoformat(row['ts']),
            host=row['host'],
            latency=row['latency'],
            error_rate=row['error_rate'],
            traffic=row['traffic'],
            is_anomaly=bool(row['is_anomaly'])
        ))

    return metrics

def get_alerts(limit: int = 50) -> List[dict]:
    """Get active alerts (anomalies) from database"""
    CHEMIN_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "network.db")
    conn = sqlite3.connect(CHEMIN_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ts, host,
               CASE
                   WHEN latency > 100 THEN 'High latency'
                   WHEN error_rate > 5 THEN 'High error rate'
                   WHEN traffic > 90 THEN 'High traffic'
                   ELSE 'Network anomaly'
               END as reason
        FROM network_metrics
        WHERE is_anomaly = 1
        ORDER BY ts DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    alerts = []
    for row in rows:
        alerts.append({
            "ts": datetime.datetime.fromisoformat(row['ts']),
            "host": row['host'],
            "reason": row['reason']
        })

    return alerts

def get_hosts() -> List[str]:
    """Get list of unique hosts in the database"""
    CHEMIN_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "network.db")
    conn = sqlite3.connect(CHEMIN_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT host FROM network_metrics ORDER BY host")
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]