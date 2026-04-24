from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


def make_mock_redis():
    mock = MagicMock()
    mock.ping.return_value = True
    return mock


@patch('main.get_redis')
def test_create_job_returns_job_id(mock_get_redis):
    """POST /jobs should return a valid job_id"""
    mock_redis = make_mock_redis()
    mock_get_redis.return_value = mock_redis

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


@patch('main.get_redis')
def test_create_job_pushes_to_queue(mock_get_redis):
    """POST /jobs should push job_id to redis queue and set status"""
    mock_redis = make_mock_redis()
    mock_get_redis.return_value = mock_redis

    response = client.post("/jobs")
    data = response.json()
    job_id = data["job_id"]

    mock_redis.lpush.assert_called_once_with("jobs", job_id)
    mock_redis.hset.assert_called_once_with(f"job:{job_id}", "status", "queued")


@patch('main.get_redis')
def test_get_job_returns_status(mock_get_redis):
    """GET /jobs/{job_id} should return job status"""
    mock_redis = make_mock_redis()
    mock_redis.hget.return_value = "queued"
    mock_get_redis.return_value = mock_redis

    response = client.get("/jobs/test-job-123")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"


@patch('main.get_redis')
def test_get_job_not_found(mock_get_redis):
    """GET /jobs/{job_id} should return error when job doesn't exist"""
    mock_redis = make_mock_redis()
    mock_redis.hget.return_value = None
    mock_get_redis.return_value = mock_redis

    response = client.get("/jobs/nonexistent-job")

    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"] == "not found"


@patch('main.get_redis')
def test_create_multiple_jobs_unique_ids(mock_get_redis):
    """Each POST /jobs should return a unique job_id"""
    mock_redis = make_mock_redis()
    mock_get_redis.return_value = mock_redis

    response1 = client.post("/jobs")
    response2 = client.post("/jobs")

    assert response1.json()["job_id"] != response2.json()["job_id"]