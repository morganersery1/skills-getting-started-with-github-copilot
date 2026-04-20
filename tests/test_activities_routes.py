from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload

    chess = payload["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess


def test_signup_success_adds_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "x@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success_removes_participant(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.delete("/activities/Chess Club/signup", params={"email": existing_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from Chess Club"}
    assert existing_email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete("/activities/Unknown Club/signup", params={"email": "x@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_registered_student_returns_404(client):
    response = client.delete("/activities/Chess Club/signup", params={"email": "not-registered@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
