"""
Test suite for Mergington High School Activities API

Uses the AAA (Arrange-Act-Assert) pattern for clear, structured tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_success(self):
        """
        Arrange: No setup needed, data is pre-populated in app
        Act: Call GET /activities
        Assert: Verify response is 200 with activities data
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) > 0

    def test_get_activities_returns_all_activity_details(self):
        """
        Arrange: No setup needed
        Act: Call GET /activities
        Assert: Verify all required fields are present for each activity
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert "Chess Club" in activities
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        """
        Arrange: Prepare a valid activity name and new student email
        Act: POST signup request
        Assert: Verify success response
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_with_nonexistent_activity(self):
        """
        Arrange: Prepare request for activity that doesn't exist
        Act: POST signup request
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered_student(self):
        """
        Arrange: Select student already registered for an activity
        Act: POST signup request for same activity
        Assert: Verify 400 error for duplicate registration
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_with_special_characters_in_activity_name(self):
        """
        Arrange: Prepare activity name with special characters (URL encoding)
        Act: POST signup request
        Assert: Verify proper handling of encoded activity names
        """
        # Arrange
        activity_name = "Science Olympiad"
        email = "science_student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self):
        """
        Arrange: Select a student registered for an activity
        Act: DELETE unregister request
        Assert: Verify success response
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"  # Already registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_from_nonexistent_activity(self):
        """
        Arrange: Prepare request for activity that doesn't exist
        Act: DELETE unregister request
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered_student(self):
        """
        Arrange: Select student not registered for the activity
        Act: DELETE unregister request
        Assert: Verify 400 error for non-existent registration
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Not registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_removes_participant_from_list(self):
        """
        Arrange: Get initial participant count, unregister a student
        Act: DELETE unregister request, then GET activities
        Assert: Verify participant was actually removed
        """
        # Arrange
        activity_name = "Tennis Club"
        email = "isabella@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])

        # Assert
        assert unregister_response.status_code == 200
        assert final_count == initial_count - 1
        assert email not in final_response.json()[activity_name]["participants"]
