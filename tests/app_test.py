"""
Unit and integration tests for the Mergington High School Activities API.

Tests are organized by endpoint using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data via fixtures
- Act: Execute the API call
- Assert: Verify response and state changes
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / (root redirection)"""

    def test_root_redirects_to_static_index(self, client):
        """
        Test: GET / should redirect to /static/index.html
        
        Arrange: TestClient ready (fixture)
        Act: Make GET request to root
        Assert: Response status is 307 (temporary redirect) with correct location
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities (retrieve all activities)"""

    def test_get_activities_returns_all_activities(self, client_with_data, test_activities):
        """
        Test: GET /activities should return all activities with correct structure
        
        Arrange: client_with_data fixture provides populated activities
        Act: Make GET request to /activities
        Assert: Response contains all test activities with expected fields
        """
        # Act
        response = client_with_data.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(test_activities)
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]

    def test_get_activities_includes_participant_list(self, client_with_data):
        """
        Test: GET /activities should include participant list for each activity
        
        Arrange: client_with_data fixture with pre-populated participants
        Act: Make GET request to /activities
        Assert: Participants list is present and matches expected data
        """
        # Act
        response = client_with_data.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_empty_participants_list(self, client_with_data):
        """
        Test: GET /activities should show empty list for activities with no participants
        
        Arrange: client_with_data fixture with "Empty Activity" having no participants
        Act: Make GET request to /activities
        Assert: Empty Activity has empty participants list
        """
        # Act
        response = client_with_data.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["Empty Activity"]["participants"] == []


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_success(self, client_with_data, test_activities):
        """
        Test: POST /signup with valid email and activity should register student
        
        Arrange: client_with_data, test_activities with Chess Club available
        Act: POST to /activities/Chess Club/signup with new email
        Assert: Response status 200, participant added to activity
        """
        # Arrange
        email = "new_student@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        assert email in test_activities[activity]["participants"]

    def test_signup_duplicate_email_rejected(self, client_with_data):
        """
        Test: POST /signup with already-registered email should return 400 error
        
        Arrange: client_with_data, "michael@mergington.edu" already in Chess Club
        Act: POST to /activities/Chess Club/signup with same email
        Assert: Response status 400 with error message
        """
        # Arrange
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client_with_data):
        """
        Test: POST /signup to non-existent activity should return 404 error
        
        Arrange: client_with_data
        Act: POST to /activities/Nonexistent Activity/signup
        Assert: Response status 404 with error message
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_updates_participant_count(self, client_with_data, test_activities):
        """
        Test: POST /signup should update participant count in activity
        
        Arrange: Empty Activity with 0/5 participants
        Act: POST to sign up one student
        Assert: Participant count increases by 1
        """
        # Arrange
        email = "new_student@mergington.edu"
        activity = "Empty Activity"
        initial_count = len(test_activities[activity]["participants"])
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert len(test_activities[activity]["participants"]) == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister"""

    def test_unregister_success(self, client_with_data, test_activities):
        """
        Test: POST /unregister with registered email should remove participant
        
        Arrange: client_with_data, "michael@mergington.edu" in Chess Club
        Act: POST to /activities/Chess Club/unregister with that email
        Assert: Response status 200, participant removed from activity
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        assert email not in test_activities[activity]["participants"]

    def test_unregister_not_found_activity(self, client_with_data):
        """
        Test: POST /unregister from non-existent activity should return 404
        
        Arrange: client_with_data
        Act: POST to /activities/Nonexistent Activity/unregister
        Assert: Response status 404 with error message
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_participant_not_registered(self, client_with_data):
        """
        Test: POST /unregister with non-registered email should return 400
        
        Arrange: client_with_data, "nonexistent@mergington.edu" not in Chess Club
        Act: POST to /activities/Chess Club/unregister with that email
        Assert: Response status 400 with error message
        """
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_updates_participant_list(self, client_with_data, test_activities):
        """
        Test: POST /unregister should remove participant from activity list
        
        Arrange: Chess Club with 2 participants initially
        Act: POST to unregister one participant
        Assert: Participant count decreases by 1
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        initial_count = len(test_activities[activity]["participants"])
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert len(test_activities[activity]["participants"]) == initial_count - 1


class TestIntegrationFlow:
    """Integration tests for complete workflows"""

    def test_full_signup_workflow(self, client_with_data, test_activities):
        """
        Test: Complete workflow - view activities → signup → verify update → view again
        
        Arrange: client_with_data with fresh activities
        Act: 1) GET /activities 2) POST /signup 3) GET /activities again
        Assert: Participant appears in second GET request
        """
        # Arrange
        email = "integration_test@mergington.edu"
        activity = "Programming Class"
        
        # Act - Step 1: Get initial activities
        response1 = client_with_data.get("/activities")
        initial_participants = response1.json()[activity]["participants"]
        
        # Act - Step 2: Sign up
        response2 = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Step 3: Get activities again
        response3 = client_with_data.get("/activities")
        final_participants = response3.json()[activity]["participants"]
        
        # Assert
        assert response2.status_code == 200
        assert email not in initial_participants
        assert email in final_participants
        assert len(final_participants) == len(initial_participants) + 1

    def test_signup_and_unregister_workflow(self, client_with_data, test_activities):
        """
        Test: Complete workflow - signup → verify → unregister → verify removal
        
        Arrange: client_with_data with Empty Activity
        Act: 1) POST /signup 2) POST /unregister 3) GET /activities
        Assert: Participant added then removed correctly
        """
        # Arrange
        email = "workflow_test@mergington.edu"
        activity = "Empty Activity"
        
        # Act - Step 1: Sign up
        response1 = client_with_data.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Step 2: Unregister
        response2 = client_with_data.post(f"/activities/{activity}/unregister?email={email}")
        
        # Act - Step 3: Verify removal
        response3 = client_with_data.get("/activities")
        final_participants = response3.json()[activity]["participants"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email not in final_participants
        assert len(final_participants) == 0

    def test_multiple_participants_signup(self, client_with_data, test_activities):
        """
        Test: Multiple students can sign up for same activity
        
        Arrange: client_with_data with Empty Activity (5 spots)
        Act: POST /signup for 3 different students
        Assert: All 3 added to participants, participant count increases
        """
        # Arrange
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        activity = "Empty Activity"
        initial_count = len(test_activities[activity]["participants"])
        
        # Act
        for email in emails:
            response = client_with_data.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Assert
        final_count = len(test_activities[activity]["participants"])
        assert final_count == initial_count + len(emails)
        for email in emails:
            assert email in test_activities[activity]["participants"]

    def test_unregister_one_of_many_participants(self, client_with_data, test_activities):
        """
        Test: Unregistering one participant doesn't affect others
        
        Arrange: Chess Club with 2 participants
        Act: Unregister one participant
        Assert: Other participant remains, count decreases by 1
        """
        # Arrange
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client_with_data.post(f"/activities/{activity}/unregister?email={email_to_remove}")
        
        # Assert
        assert response.status_code == 200
        assert email_to_remove not in test_activities[activity]["participants"]
        assert email_to_keep in test_activities[activity]["participants"]
