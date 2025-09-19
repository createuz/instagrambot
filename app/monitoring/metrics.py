# app/monitoring/metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Updates
UPDATES_TOTAL = Counter("bot_updates_total", "Total incoming updates processed")
UPDATES_FAILED = Counter("bot_updates_failed_total", "Total updates that failed during processing")
# Processing time for updates
UPDATE_PROCESS_SECONDS = Histogram("bot_update_processing_seconds", "Time spent processing updates", buckets=(0.005,0.01,0.025,0.05,0.1,0.25,0.5,1.0,2.5,5.0,10.0))

# Broadcast
BROADCAST_SENT = Counter("bot_broadcast_sent_total", "Total messages successfully sent in broadcasts")
BROADCAST_FAILED = Counter("bot_broadcast_failed_total", "Total failed send attempts in broadcasts")

# Health gauges
BOT_UP = Gauge("bot_up", "Bot up (1 = up, 0 = down)")
DB_UP = Gauge("db_up", "Database reachable (1 = yes, 0 = no)")
REDIS_UP = Gauge("redis_up", "Redis reachable (1 = yes, 0 = no)")
