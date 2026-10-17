import pytest
from app.exporters.pdf_exporter import MangaPDFExporter

def test_manga_pdf_generation_b5():
    exporter = MangaPDFExporter(page_size_name="B5", reading_direction="right-to-left")
    assert exporter.width == 516
    assert exporter.height == 729

    sample_pages = [
        {
            "page_number": 1,
            "panels": [
                {
                    "panel_number": 1,
                    "script": "Opening shot",
                    "dialogue": [{"speaker_name": "Ren", "text": "The storm is arriving.", "bubble_type": "speech", "x": 20.0, "y": 20.0}],
                    "narration": [{"text": "Tokyo, 2045.", "box_type": "caption", "x": 5.0, "y": 5.0}],
                    "sound_effects": [{"text": "BOOM", "sfx_type": "ambient", "x": 60.0, "y": 60.0}]
                },
                {
                    "panel_number": 2,
                    "script": "Close-up",
                    "dialogue": [{"speaker_name": "Vesper", "text": "Target locked.", "bubble_type": "thought", "x": 15.0, "y": 15.0}],
                    "narration": [],
                    "sound_effects": []
                }
            ]
        }
    ]

    pdf_bytes = exporter.generate_pdf(
        project_title="Spirit Blade",
        chapter_title="Episode 1: The Sparks",
        chapter_number=1,
        pages_data=sample_pages,
        include_cover=True
    )

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    # PDF magic header %PDF-
    assert pdf_bytes.startswith(b"%PDF-")
