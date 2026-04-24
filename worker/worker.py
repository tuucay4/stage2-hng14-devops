import redis
import time
import os
import signal
import sys


def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )


def handle_shutdown(signum, frame):
    print("Shutting down worker gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(r, job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


r = get_redis()


while True:
    job = r.brpop("jobs", timeout=5)
    if job:
        _, job_id = job
        process_job(r, job_id)
