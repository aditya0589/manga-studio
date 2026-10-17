import os
import io
import math
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4, B5
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image

from app.core.logging import logger
from app.storage import storage

PAGE_SIZES = {
    "B5": (516, 729),     # Standard Japanese Manga Tankobon / Magazine ratio
    "A4": (595, 842),
    "Letter": (612, 792)
}

class MangaPDFExporter:
    """Renders professional manga chapters to PDF with covers, panels, speech bubbles, and sound effects."""

    def __init__(self, page_size_name: str = "B5", reading_direction: str = "right-to-left"):
        self.page_size = PAGE_SIZES.get(page_size_name, PAGE_SIZES["B5"])
        self.width, self.height = self.page_size
        self.reading_direction = reading_direction.lower()

    def _draw_speech_bubble(self, c: canvas.Canvas, text: str, speaker: str, x: float, y: float, bubble_type: str = "speech"):
        """Draws manga speech bubble or thought bubble with text."""
        c.saveState()
        # Measure bubble size
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            lines = [text]

        max_len = max(len(l) for l in lines)
        bubble_width = min(220, max(90, max_len * 7 + 24))
        line_height = 13
        bubble_height = len(lines) * line_height + 22

        # Clamp coordinates to page boundaries
        bx = max(20, min(self.width - bubble_width - 20, x))
        by = max(20, min(self.height - bubble_height - 20, y))

        if bubble_type == "thought":
            c.setStrokeColor(colors.HexColor("#333333"))
            c.setFillColor(colors.HexColor("#FFFFFF"))
            c.setLineWidth(1.5)
            c.setDash(3, 3)
            c.roundRect(bx, by, bubble_width, bubble_height, 14, fill=1, stroke=1)
        else: # speech / shout
            c.setStrokeColor(colors.HexColor("#000000"))
            c.setFillColor(colors.HexColor("#FFFFFF"))
            c.setLineWidth(2.2)
            c.roundRect(bx, by, bubble_width, bubble_height, 12, fill=1, stroke=1)
            # Pointer tail
            p = c.beginPath()
            p.moveTo(bx + 15, by)
            p.lineTo(bx + 25, by - 8)
            p.lineTo(bx + 32, by)
            c.drawPath(p, fill=1, stroke=1)

        # Speaker label
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#6b21a8"))
        c.drawString(bx + 8, by + bubble_height - 11, speaker[:20].upper())

        # Dialogue text
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#000000"))
        text_y = by + bubble_height - 24
        for l in lines:
            c.drawString(bx + 8, text_y, l[:38])
            text_y -= line_height

        c.restoreState()

    def _draw_narration_box(self, c: canvas.Canvas, text: str, x: float, y: float):
        """Draws dark narration caption box."""
        c.saveState()
        box_width = min(240, max(120, len(text) * 6 + 20))
        box_height = 26
        bx = max(20, min(self.width - box_width - 20, x))
        by = max(20, min(self.height - box_height - 20, y))

        c.setFillColor(colors.HexColor("#0f172a"))
        c.setStrokeColor(colors.HexColor("#7c3aed"))
        c.setLineWidth(1.5)
        c.rect(bx, by, box_width, box_height, fill=1, stroke=1)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#f8fafc"))
        c.drawString(bx + 8, by + 9, text[:45])
        c.restoreState()

    def _draw_sound_effect(self, c: canvas.Canvas, text: str, x: float, y: float):
        """Draws dramatic stylized sound effect text."""
        c.saveState()
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#7c3aed"))
        c.drawString(x, y, text.upper())
        c.restoreState()

    def generate_pdf(
        self,
        project_title: str,
        chapter_title: str,
        chapter_number: int,
        pages_data: List[Dict[str, Any]],
        include_cover: bool = True
    ) -> bytes:
        """Assembles and generates the full PDF binary."""
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=self.page_size)

        total_pages = len(pages_data) + (1 if include_cover else 0)
        current_page_idx = 1

        # Page 1: Stylized Studio Cover
        if include_cover:
            # Dark manga background
            c.setFillColor(colors.HexColor("#0a0b0e"))
            c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

            # Elegant violet accent frames
            c.setStrokeColor(colors.HexColor("#7c3aed"))
            c.setLineWidth(3)
            c.rect(28, 28, self.width - 56, self.height - 56, fill=0, stroke=1)

            c.setStrokeColor(colors.HexColor("#2e3344"))
            c.setLineWidth(1)
            c.rect(34, 34, self.width - 68, self.height - 68, fill=0, stroke=1)

            # Cover Title
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(colors.HexColor("#ffffff"))
            c.drawCentredString(self.width / 2, self.height * 0.72, project_title)

            # Subtitle / Chapter
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(colors.HexColor("#a78bfa"))
            c.drawCentredString(self.width / 2, self.height * 0.65, f"Chapter {chapter_number}: {chapter_title}")

            # Badge
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#94a3b8"))
            dir_label = "Manga Reading Order: Right-to-Left (<-)" if self.reading_direction == "right-to-left" else "Reading Order: Left-to-Right (->)"
            c.drawCentredString(self.width / 2, self.height * 0.58, dir_label)

            # Footer
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.HexColor("#64748b"))
            c.drawCentredString(self.width / 2, 50, "CREATED WITH AI MANGA STUDIO - PUBLISHING ENGINE")

            c.showPage()
            current_page_idx += 1

        # Chapter Content Pages
        for page in pages_data:
            p_num = page.get("page_number", current_page_idx)
            panels = page.get("panels", [])

            # Page background
            c.setFillColor(colors.HexColor("#0f1117"))
            c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

            # Draw page header & footer
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#64748b"))
            c.drawString(30, self.height - 20, f"{project_title} - {chapter_title}")
            c.drawRightString(self.width - 30, 16, f"Page {p_num} of {total_pages}")

            # Calculate 2x2 grid panel coordinates
            margin_x = 24
            margin_y = 30
            gap = 12
            usable_w = self.width - 2 * margin_x
            usable_h = self.height - 2 * margin_y - 20 # account for headers

            col_w = (usable_w - gap) / 2
            row_h = (usable_h - gap) / 2

            # Layout panels in reading direction
            # If right-to-left: panel 1 is top-right, panel 2 is top-left, panel 3 is bottom-right, panel 4 is bottom-left
            positions = [
                (margin_x + col_w + gap, margin_y + row_h + gap), # Top-Right
                (margin_x, margin_y + row_h + gap),               # Top-Left
                (margin_x + col_w + gap, margin_y),               # Bottom-Right
                (margin_x, margin_y)                              # Bottom-Left
            ] if self.reading_direction == "right-to-left" else [
                (margin_x, margin_y + row_h + gap),               # Top-Left
                (margin_x + col_w + gap, margin_y + row_h + gap), # Top-Right
                (margin_x, margin_y),                              # Bottom-Left
                (margin_x + col_w + gap, margin_y)                # Bottom-Right
            ]

            for idx, panel in enumerate(panels[:4]):
                px, py = positions[idx]

                # Draw panel outer frame
                c.setStrokeColor(colors.HexColor("#2a2f40"))
                c.setLineWidth(2)
                c.rect(px, py, col_w, row_h, fill=0, stroke=1)

                # Render Artwork if exists
                asset_info = panel.get("asset_info") or panel.get("asset")
                img_drawn = False
                if asset_info and asset_info.get("storage_key"):
                    try:
                        abs_path = storage.get_absolute_path(asset_info["storage_key"])
                        if os.path.exists(abs_path):
                            c.drawImage(abs_path, px + 2, py + 2, width=col_w - 4, height=row_h - 4, preserveAspectRatio=False)
                            img_drawn = True
                    except Exception as e:
                        logger.warning(f"Failed to embed image in PDF: {e}")

                if not img_drawn:
                    # Draw stylish placeholder panel with panel number
                    c.setFillColor(colors.HexColor("#161922"))
                    c.rect(px + 2, py + 2, col_w - 4, row_h - 4, fill=1, stroke=0)
                    c.setFont("Helvetica-Bold", 12)
                    c.setFillColor(colors.HexColor("#8b5cf6"))
                    c.drawCentredString(px + col_w / 2, py + row_h / 2, f"PANEL {panel.get('panel_number', idx + 1)}")

                # Overlay dialogue, narration, sound effects
                for d in panel.get("dialogue", []):
                    rel_x = px + (d.get("x", 20.0) / 100.0) * col_w
                    rel_y = py + (d.get("y", 20.0) / 100.0) * row_h
                    self._draw_speech_bubble(c, d.get("text", ""), d.get("speaker_name", "Character"), rel_x, rel_y, d.get("bubble_type", "speech"))

                for n in panel.get("narration", []):
                    rel_x = px + (n.get("x", 10.0) / 100.0) * col_w
                    rel_y = py + (n.get("y", 10.0) / 100.0) * row_h
                    self._draw_narration_box(c, n.get("text", ""), rel_x, rel_y)

                for sfx in panel.get("sound_effects", []):
                    rel_x = px + (sfx.get("x", 50.0) / 100.0) * col_w
                    rel_y = py + (sfx.get("y", 50.0) / 100.0) * row_h
                    self._draw_sound_effect(c, sfx.get("text", "SFX"), rel_x, rel_y)

            c.showPage()
            current_page_idx += 1

        c.save()
        return pdf_buffer.getvalue()
