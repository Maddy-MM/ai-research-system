from prometheus_client import Counter, Histogram

# Counter: ever-increasing. Use for total requests, errors, pipeline runs.
PIPELINE_REQUESTS_TOTAL = Counter(
    name="pipeline_requests_total",
    documentation="Total number of research pipeline runs",
    labelnames=["status"],
)

# Histogram: tracks value distribution (e.g. latency).
# buckets are in seconds — tuned for a pipeline that takes 10–60s.
PIPELINE_DURATION_SECONDS = Histogram(
    name="pipeline_duration_seconds",
    documentation="End-to-end research pipeline duration in seconds",
    buckets=[5, 10, 20, 30, 45, 60, 90, 120],
)

PIPELINE_STEP_DURATION_SECONDS = Histogram(
    name="pipeline_step_duration_seconds",
    documentation="Duration of each individual pipeline step in seconds",
    labelnames=["step"],
    buckets=[2, 5, 10, 20, 30, 60],
)