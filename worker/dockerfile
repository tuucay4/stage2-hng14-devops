FROM python:3.11-alpine AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir pip==24.0 && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S appuser -G app

COPY --from=builder /install /usr/local
COPY worker.py .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), password=os.getenv('REDIS_PASSWORD'), decode_responses=True); r.ping()"

CMD ["python", "worker.py"]