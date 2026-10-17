import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest.mark.asyncio
async def test_full_end_to_end_manga_studio_pipeline():
    """Comprehensive E2E smoke test verifying full user journey:
    Register -> Project Creation -> Document Upload -> Character Bible ->
    Full Chapter Generation via LangGraph -> Manga Editor Panel Customization -> PDF Export.
    """
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login
        email = f"mangaka_e2e_{uuid.uuid4().hex[:6]}@studiomanga.com"
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "manga_secure_pass_123"
        })
        assert reg_res.status_code == 201, reg_res.text
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Project
        create_proj_res = await client.post("/api/v1/projects", headers=headers, json={
            "title": "Eclipse of the Soul Forger",
            "genre": "Fantasy and dark fantasy",
            "art_style": "Traditional Manga B&W",
            "reading_direction": "right-to-left",
            "target_audience": "Shonen",
            "synopsis": "Ren Kurogane awakens a forbidden blade spirit to shatter the imperial siege."
        })
        assert create_proj_res.status_code == 201
        project_id = create_proj_res.json()["id"]

        # 3. Upload Manuscript Document
        sample_doc = b"The rain beat against the wooden slats of the forge. Ren clenched his fist around the broken iron."
        upload_res = await client.post(
            f"/api/v1/projects/{project_id}/uploads",
            headers=headers,
            files={"file": ("manuscript.txt", sample_doc, "text/plain")},
            data={"document_type": "manuscript"}
        )
        assert upload_res.status_code == 200
        doc_data = upload_res.json()
        assert "broken iron" in doc_data["extracted_text"]

        # 4. Create Canonical Character
        char_res = await client.post(
            f"/api/v1/projects/{project_id}/characters",
            headers=headers,
            json={
                "name": "Ren Kurogane",
                "role": "Protagonist",
                "appearance": "Jet-black spiky hair with white bangs, piercing mercury eyes",
                "canon_data": {
                    "hair": "Jet-black with white bangs",
                    "eyes": "Mercury silver",
                    "visual_consistency_rules": ["White bangs always on right side"]
                }
            }
        )
        assert char_res.status_code == 201
        char_id = char_res.json()["id"]

        # 5. Generate Full Chapter with LangGraph Workflow
        gen_chap_res = await client.post(
            f"/api/v1/projects/{project_id}/chapters/generate",
            headers=headers,
            json={
                "title": "Chapter 1: The Midnight Awakening",
                "synopsis": "Ren confronts the imperial enforcer in the burning forge.",
                "order_index": 1
            }
        )
        assert gen_chap_res.status_code == 200
        job_data = gen_chap_res.json()
        chapter_id = job_data["chapter_id"]

        # Wait briefly for background generation task
        import asyncio
        for _ in range(15):
            await asyncio.sleep(0.5)
            ch_status_res = await client.get(f"/api/v1/chapters/{chapter_id}", headers=headers)
            if ch_status_res.status_code == 200:
                ch_obj = ch_status_res.json()
                if len(ch_obj["pages"]) > 0:
                    break

        # 6. Verify Pages and Panels were assembled
        ch_res = await client.get(f"/api/v1/chapters/{chapter_id}", headers=headers)
        assert ch_res.status_code == 200
        ch_data = ch_res.json()
        assert len(ch_data["pages"]) > 0
        first_page = ch_data["pages"][0]
        assert len(first_page["panels"]) > 0
        panel_to_edit = first_page["panels"][0]

        # 7. Edit Dialogue & Sound Effects in Manga Editor
        edit_panel_res = await client.patch(
            f"/api/v1/panels/{panel_to_edit['id']}",
            headers=headers,
            json={
                "dialogue": [{
                    "speaker_name": "Ren",
                    "text": "The spirit blade will not yield to tyranny!",
                    "bubble_type": "speech",
                    "x": 20.0,
                    "y": 20.0
                }],
                "narration": [{
                    "text": "The smithy burns around them.",
                    "box_type": "caption",
                    "x": 6.0,
                    "y": 6.0
                }],
                "sound_effects": [{
                    "text": "SLASHHH!",
                    "sfx_type": "impact",
                    "x": 50.0,
                    "y": 50.0
                }]
            }
        )
        assert edit_panel_res.status_code == 200
        updated_panel = edit_panel_res.json()
        assert updated_panel["dialogue"][0]["text"] == "The spirit blade will not yield to tyranny!"

        # 8. Regenerate Single Panel Artwork
        regen_res = await client.post(
            f"/api/v1/panels/{panel_to_edit['id']}/regenerate",
            headers=headers,
            json={"custom_prompt": "Epic climactic manga clash, glowing spirit katana, flying sparks"}
        )
        assert regen_res.status_code == 200
        regen_panel = regen_res.json()
        assert regen_panel["status"] == "generated"
        assert regen_panel["image_url"] is not None

        # 9. Export to High-Quality PDF with Cover and Reading Flow
        export_res = await client.post(
            f"/api/v1/chapters/{chapter_id}/exports",
            headers=headers,
            json={
                "format": "pdf",
                "page_size": "B5",
                "reading_direction": "right-to-left",
                "include_cover": True
            }
        )
        assert export_res.status_code == 200
        exp_data = export_res.json()
        export_id = exp_data["id"]

        # 10. Download & Validate PDF Binary
        dl_res = await client.get(f"/api/v1/exports/{export_id}/download")
        assert dl_res.status_code == 200
        assert dl_res.headers["content-type"] == "application/pdf"
        assert dl_res.content.startswith(b"%PDF-")
        assert len(dl_res.content) > 5000
