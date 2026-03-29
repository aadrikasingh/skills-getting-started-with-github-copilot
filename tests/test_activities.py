from src.app import activities


class TestRootRedirect:
    def test_root_redirects_to_static_index(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9

    def test_activity_has_expected_fields(self, client):
        response = client.get("/activities")
        data = response.json()
        for name, info in data.items():
            assert "description" in info
            assert "schedule" in info
            assert "max_participants" in info
            assert "participants" in info

    def test_known_activity_content(self, client):
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert chess["max_participants"] == 12
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]
        # Verify participant was actually added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client):
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_increases_participant_count(self, client):
        before = len(activities["Programming Class"]["participants"])
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "newbie@mergington.edu"},
        )
        after = len(activities["Programming Class"]["participants"])
        assert after == before + 1


class TestUnregister:
    def test_unregister_success(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_not_signed_up_returns_404(self, client):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "unknown@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_invalid_activity_returns_404(self, client):
        response = client.delete(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_decreases_participant_count(self, client):
        before = len(activities["Soccer Team"]["participants"])
        client.delete(
            "/activities/Soccer Team/signup",
            params={"email": "liam@mergington.edu"},
        )
        after = len(activities["Soccer Team"]["participants"])
        assert after == before - 1
