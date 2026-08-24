"""
Pytest configuration and shared fixtures for FastAPI tests.

This module provides:
- TestClient instance for making HTTP requests to the FastAPI app
- Test data fixtures with various activity states
- Fixtures for integration testing with pre-populated data
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as original_activities


@pytest.fixture
def client():
    """
    Fixture: Provide a TestClient for the FastAPI app.
    
    Arrange: Client is ready to use for API calls
    """
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Fixture: Provide fresh, in-memory activities dict for each test.
    
    Arrange: Initialize a clean activities dict that mirrors the app's structure
    but is isolated per test to prevent cross-test pollution.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Empty Activity": {
            "description": "Activity with no participants",
            "schedule": "Mondays, 4:00 PM - 5:00 PM",
            "max_participants": 5,
            "participants": []
        },
        "Full Activity": {
            "description": "Activity at max capacity",
            "schedule": "Wednesdays, 3:00 PM - 4:00 PM",
            "max_participants": 2,
            "participants": ["student1@mergington.edu", "student2@mergington.edu"]
        }
    }


@pytest.fixture
def client_with_data(client, test_activities, monkeypatch):
    """
    Fixture: Provide a TestClient with pre-populated test activities.
    
    Arrange: Inject test_activities into the app's activities dict so API calls
    see the test data instead of the original in-memory dict.
    """
    monkeypatch.setattr("src.app.activities", test_activities)
    return client
