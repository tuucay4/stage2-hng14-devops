# FIXES.md

---

## 1. API Service ([api/main.py](https://github.com/tuucay4/stage2-hng14-devops/blob/main/api/main.py))

| Line(s) | Issue | Fix |
|---|---|---|
| 9 | **Hardcoded Connection:** `r = redis.Redis(host="localhost", port=6379)` prevented the API from reaching Redis inside a Docker network. | Changed to a dynamic `get_redis()` function using `os.getenv("REDIS_HOST", "redis")`. |
| 9 | **Missing Authentication:** The original connection ignored the `REDIS_PASSWORD` defined in the environment. | Added `password=os.getenv("REDIS_PASSWORD")` to the Redis initialization. |

---

## 2. Worker Service ([worker/worker.py](https://github.com/tuucay4/stage2-hng14-devops/blob/main/worker/worker.py))

| Line(s) | Issue | Fix |
|---|---|---|
| 6 | **Network Isolation:** Hardcoded `localhost` prevented the worker from connecting to the Redis container. | Implemented `os.getenv` for `REDIS_HOST` and `REDIS_PORT`. |
| 6 | **Security Gap:** No password was used to connect to the secured Redis instance. | Updated connection logic to include `os.getenv("REDIS_PASSWORD")`. |
| 15–20 | **Zombie Processes:** No signal handling meant the worker couldn't shut down gracefully during a rolling update. | Added `signal.signal` handlers for `SIGTERM` and `SIGINT` to allow clean exits. |

---

## 3. Frontend Service ([frontend/app.js](https://github.com/tuucay4/stage2-hng14-devops/blob/main/frontend/app.js))

| Line(s) | Issue | Fix |
|---|---|---|
| 6 | **Inaccessible Backend:** `API_URL` was hardcoded to `localhost`, which fails when the container tries to route traffic to the API service. | Refactored to `process.env.API_URL \|\| "http://api:8000"` for dynamic resolution. |
| 14, 23 | **Silent Failures:** Errors in API calls were caught but not logged, making debugging impossible. | Added `console.error` to output the specific `err.message` to the container logs. |

---

## 4. Security (`api/.env`)

| File | Issue | Fix |
|---|---|---|
| `api/.env` | **Exposed Secret:** A real `REDIS_PASSWORD` was committed directly to the repository. | Deleted the file, added `.env` to `.gitignore`, and created `.env.example` with placeholder values. |