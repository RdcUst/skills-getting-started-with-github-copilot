import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test cases for the Activities API endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200

        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check that each activity has the required fields
        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_specific_activity(self):
        """Test that specific activities exist and have correct structure"""
        response = client.get("/activities")
        activities = response.json()

        # Test Chess Club structure
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) >= 0

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        # Use a unique email to avoid conflicts
        test_email = "test.student@mergington.edu"

        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": test_email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_duplicate(self):
        """Test signing up for the same activity twice"""
        test_email = "duplicate.test@mergington.edu"

        # First signup should succeed
        response1 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": test_email}
        )
        assert response1.status_code == 200

        # Second signup should fail
        response2 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": test_email}
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_unregister_successful(self):
        """Test successful unregistration from an activity"""
        test_email = "unregister.test@mergington.edu"

        # First sign up
        client.post(
            "/activities/Tennis/signup",
            params={"email": test_email}
        )

        # Then unregister
        response = client.delete(
            "/activities/Tennis/unregister",
            params={"email": test_email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert "Tennis" in result["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregistering a student who is not signed up"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "notsignedup@mergington.edu"}
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"]

    def test_root_redirect(self):
        """Test that root path redirects to static index"""
        # TestClient follows redirects by default, so we need to disable that
        client_no_redirect = TestClient(app, follow_redirects=False)
        response = client_no_redirect.get("/")
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_static_files_served(self):
        """Test that static files are served correctly"""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "Mergington High School" in response.text

    def test_activities_data_integrity(self):
        """Test that activities data remains consistent"""
        # Get initial state
        response1 = client.get("/activities")
        initial_activities = response1.json()

        # Make some changes
        test_email = "integrity.test@mergington.edu"
        client.post("/activities/Gym%20Class/signup", params={"email": test_email})
        client.delete("/activities/Gym%20Class/unregister", params={"email": test_email})

        # Get final state
        response2 = client.get("/activities")
        final_activities = response2.json()

        # Structure should be the same
        assert set(initial_activities.keys()) == set(final_activities.keys())
        for activity in initial_activities:
            assert set(initial_activities[activity].keys()) == set(final_activities[activity].keys())