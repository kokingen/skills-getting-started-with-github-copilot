"""Backend tests for the Mergington High School API (Arrange-Act-Assert)."""

from src import app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange / Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert len(data) == len(app_module.activities)
    for details in data.values():
        assert {"description", "schedule", "max_participants", "participants"} <= details.keys()


def test_signup_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_twice_is_rejected(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert app_module.activities["Chess Club"]["participants"].count(email) == 1


def test_signup_unknown_activity_returns_404(client):
    # Act
    response = client.post("/activities/Underwater Basket Weaving/signup", params={"email": "a@mergington.edu"})

    # Assert
    assert response.status_code == 404


def test_signup_full_activity_is_rejected(client):
    # Arrange
    activity = app_module.activities["Chess Club"]
    activity["participants"] = [f"s{i}@mergington.edu" for i in range(activity["max_participants"])]

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "late@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_removes_participant(client):
    # Arrange
    email = "daniel@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_not_signed_up_returns_400(client):
    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": "nobody@mergington.edu"})

    # Assert
    assert response.status_code == 400


def test_unregister_unknown_activity_returns_404(client):
    # Act
    response = client.delete("/activities/Nope/unregister", params={"email": "a@mergington.edu"})

    # Assert
    assert response.status_code == 404
