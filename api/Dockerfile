FROM python:3.11-alpine AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir pip==24.0 && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S appuser -G app

COPY --from=builder /install /usr/local
COPY main.py .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]