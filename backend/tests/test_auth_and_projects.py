import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_auth_registration_login_and_me():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        test_email = f"mangaka_{uuid.uuid4().hex[:6]}@example.com"
        # Register new user
        reg_payload = {"email": test_email, "password": "secure_password_123"}
        reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201, reg_res.text
        data = reg_res.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_email
        token = data["access_token"]

        # Duplicate registration rejected
        dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_res.status_code == 400

        # Login
        login_res = await client.post("/api/v1/auth/login", json=reg_payload)
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # Get me
        headers = {"Authorization": f"Bearer {token}"}
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == test_email

@pytest.mark.asyncio
async def test_project_crud_and_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        e1 = f"u1_{uuid.uuid4().hex[:6]}@studio.com"
        e2 = f"u2_{uuid.uuid4().hex[:6]}@studio.com"
        # Register User 1
        u1_res = await client.post("/api/v1/auth/register", json={"email": e1, "password": "password123"})
        assert u1_res.status_code == 201
        token_u1 = u1_res.json()["access_token"]
        headers_u1 = {"Authorization": f"Bearer {token_u1}"}

        # Register User 2
        u2_res = await client.post("/api/v1/auth/register", json={"email": e2, "password": "password123"})
        assert u2_res.status_code == 201
        token_u2 = u2_res.json()["access_token"]
        headers_u2 = {"Authorization": f"Bearer {token_u2}"}

        # User 1 creates project
        create_res = await client.post("/api/v1/projects", headers=headers_u1, json={
            "title": "Chrono Blade",
            "genre": "Fantasy and dark fantasy",
            "art_style": "Traditional Manga B&W",
            "reading_direction": "right-to-left",
            "target_audience": "Shonen",
            "synopsis": "A rogue chronomancer seeks to undo the kingdom's fall."
        })
        assert create_res.status_code == 201
        p_data = create_res.json()
        project_id = p_data["id"]
        assert p_data["title"] == "Chrono Blade"

        # User 1 can view project
        get_res = await client.get(f"/api/v1/projects/{project_id}", headers=headers_u1)
        assert get_res.status_code == 200

        # User 2 CANNOT access User 1's project (multi-user isolation)
        forbidden_res = await client.get(f"/api/v1/projects/{project_id}", headers=headers_u2)
        assert forbidden_res.status_code == 403

        # User 1 updates project
        update_res = await client.patch(f"/api/v1/projects/{project_id}", headers=headers_u1, json={
            "title": "Chrono Blade: Rebirth"
        })
        assert update_res.status_code == 200
        assert update_res.json()["title"] == "Chrono Blade: Rebirth"
