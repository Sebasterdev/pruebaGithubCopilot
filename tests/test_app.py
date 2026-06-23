from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success():
    email = "test_student@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup?email=test_student%40mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    refresh = client.get("/activities")
    activity = refresh.json()["Chess Club"]
    assert email in activity["participants"]


def test_signup_for_activity_duplicate_returns_400():
    email = "duplicate_student@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    email = "remove_student@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}

    refresh = client.get("/activities")
    activity = refresh.json()["Chess Club"]
    assert email not in activity["participants"]


def test_remove_participant_missing_returns_404():
    response = client.delete("/activities/Chess%20Club/participants?email=missing_student%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
