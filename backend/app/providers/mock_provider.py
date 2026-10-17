import io
import json
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

from app.providers.llm_base import BaseLLMProvider
from app.providers.image_base import BaseImageProvider

class MockLLMProvider(BaseLLMProvider):
    def _extract_context(self, prompt: str) -> Dict[str, Any]:
        """Extract story parameters from prompts to generate authentic, non-static manga content."""
        prompt_lower = prompt.lower()
        import re

        # Extract Project Title
        title_match = re.search(r"Project Title:\s*([^\n\r]+)", prompt, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            # Fallback check for common title patterns
            if "shipuden of the sea" in prompt_lower or "shipuden" in prompt_lower:
                title = "Shipuden of the sea"
            else:
                title = "Chronicles of Destiny"

        # Extract Genre
        genre_match = re.search(r"Genre:\s*([^\n\r]+)", prompt, re.IGNORECASE)
        genre = genre_match.group(1).strip() if genre_match else "Action Fantasy"

        # Extract Characters
        char_match = re.search(r"(?:Existing )?Characters:\s*([^\n\r]+)", prompt, re.IGNORECASE)
        char_str = char_match.group(1).strip() if char_match else ""
        found_chars = []
        if char_str and char_str != "[]":
            clean_names = re.findall(r"['\"]([^'\"]+)['\"]", char_str)
            if not clean_names:
                clean_names = [n.strip() for n in char_str.strip("[]").split(",") if n.strip()]
            found_chars = [n for n in clean_names if n.lower() not in ("none", "null")]

        # Determine Theme
        combined_text = (prompt_lower + " " + title.lower())
        if any(w in combined_text for w in ["sea", "ocean", "ship", "pirate", "sail", "water", "marine", "navy", "shipuden", "nautical", "island"]):
            theme = "nautical"
        elif any(w in combined_text for w in ["cyber", "neon", "tech", "hacker", "future", "android", "mech", "sci-fi"]):
            theme = "cyberpunk"
        elif any(w in combined_text for w in ["ninja", "shinobi", "dojo", "jutsu", "martial"]):
            theme = "ninja"
        elif any(w in combined_text for w in ["vampire", "demon", "curse", "ghoul", "blood", "goth"]):
            theme = "dark_fantasy"
        else:
            theme = "fantasy"

        # Assign character names based on context
        if len(found_chars) >= 2:
            protagonist = found_chars[0]
            supporter = found_chars[1]
        elif len(found_chars) == 1:
            protagonist = found_chars[0]
            supporter = "Yumico" if theme == "nautical" else "Aoi"
        else:
            if theme == "nautical":
                protagonist = "Shinobu"
                supporter = "Yumico"
            elif theme == "cyberpunk":
                protagonist = "Ren"
                supporter = "Vesper"
            else:
                protagonist = "Kenji"
                supporter = "Kaede"

        # Character appearance rules
        if protagonist.lower() == "shinobu":
            protagonist_desc = "Dark brown hair skinny guy wearing a black hoodie with piercing amber eyes"
        elif protagonist.lower() == "ren kurogane":
            protagonist_desc = "Jet-black spiky hair with white streak, silver eyes, dark haori"
        elif theme == "nautical":
            protagonist_desc = f"{protagonist}, fearless young mariner with dark brown hair, wearing a black hoodie and maritime gear"
        else:
            protagonist_desc = f"{protagonist}, determined manga protagonist with spiky dark hair and intense eyes"

        if supporter.lower() in ("yumico", "yumiko"):
            supporter_desc = "Fair skinned short girl with dark hair wearing a white frock and brass navigator compass"
        elif theme == "nautical":
            supporter_desc = f"{supporter}, young sea navigator with windblown hair and nautical charts"
        else:
            supporter_desc = f"{supporter}, skilled ally with keen analytical gaze"

        return {
            "title": title,
            "genre": genre,
            "theme": theme,
            "protagonist": protagonist,
            "supporter": supporter,
            "protagonist_desc": protagonist_desc,
            "supporter_desc": supporter_desc
        }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format_json: bool = False
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        ctx = self._extract_context(prompt)
        p = ctx["protagonist"]
        s = ctx["supporter"]
        title = ctx["title"]
        theme = ctx["theme"]

        # Handle Story Analysis & Bible
        if "analyze" in prompt_lower or "bible" in prompt_lower or "synopsis" in prompt_lower or "ingest" in prompt_lower or "architect" in prompt_lower:
            if theme == "nautical":
                data = {
                    "premise": f"Across the boundless tempest seas of {title}, a fearless crew defies the iron naval blockade to reach the uncharted mythical horizons.",
                    "synopsis": f"{p}, a daring mariner in a black hoodie, and {s}, an observant sea navigator, sail into dangerous waters aboard their vessel. Facing relentless oceanic squalls and tyrannical fleet commanders, they fight to unlock the ancient tidal secret before the Grand Armada conquers the ocean.",
                    "world_rules": [
                        "Storm tides can only be navigated by sensing currents through ancient celestial sea astrolabes.",
                        "Using spirit-wave maneuvers expends vital stamina, requiring sea mariners to pace their surges.",
                        "Admiralty war ironclads are armored with volcanic steel impervious to standard harpoons."
                    ],
                    "factions_and_locations": [
                        {"name": "The Grand Admiralty", "type": "Faction", "description": "Oppressive naval armada wielding ironclad warships and steam cannons."},
                        {"name": "Tempest Strait", "type": "Location", "description": "A treacherous ocean passage with roaring 40-foot waves and misty coral reefs."}
                    ],
                    "timeline_events": [
                        {"era": "The Calamity Tide", "event": "Ancient sea gates broke, unleashing eternal tempest currents across the world."},
                        {"era": "Present Day", "event": f"{p} and {s} set sail on {title} to break through the blockade."}
                    ],
                    "characters": [
                        {
                            "name": p,
                            "role": "Protagonist",
                            "personality": "Fearless, fiercely loyal to their shipmates, quick-witted in dangerous tides.",
                            "appearance": ctx["protagonist_desc"],
                            "canon_data": {
                                "hair": "Dark brown windswept hair",
                                "eyes": "Amber determined eyes",
                                "clothing": "Black hoodie and rugged sailor trousers",
                                "accessories": ["Weathered brass mariner compass", "Waterproof deck gloves"],
                                "visual_consistency_rules": ["Black hoodie hood is down on deck, raised during battle."]
                            }
                        },
                        {
                            "name": s,
                            "role": "Supporting",
                            "personality": "Sharp-eyed, quiet yet courageous, master of stellar navigation.",
                            "appearance": ctx["supporter_desc"],
                            "canon_data": {
                                "hair": "Dark brown hair",
                                "eyes": "Curious hazel eyes",
                                "clothing": "White frock with leather chart pouch",
                                "accessories": ["Telescope", "Leather star atlas"],
                                "visual_consistency_rules": ["Always keeps her sea atlas secure at her hip."]
                            }
                        }
                    ],
                    "plot_arcs": [
                        {"title": "The Maiden Voyage", "summary": f"{p} and {s} outmaneuver an Admiralty patrol ship in a midnight squall.", "order_index": 1},
                        {"title": "The Maelstrom Gate", "summary": f"Breaching the guarded oceanic rift to reach the lost continent.", "order_index": 2}
                    ]
                }
            else:
                data = {
                    "premise": f"In the world of {title}, an exiled warrior awakens legendary abilities to overthrow a corrupt regime.",
                    "synopsis": f"{p} and their ally {s} embark on a high-stakes quest across hostile territory, mastering forbidden arts to defend their homeland from encroaching dark forces.",
                    "world_rules": [
                        "Aura techniques require extreme concentration and deplete physical stamina.",
                        "Imperial guardians wear cursed porcelain armor negating kinetic strikes."
                    ],
                    "factions_and_locations": [
                        {"name": "Imperial Guard", "type": "Faction", "description": "Authoritarian enforcers maintaining iron rule."},
                        {"name": "The High Citadel", "type": "Location", "description": "Towering mountain fortress surrounded by storm clouds."}
                    ],
                    "timeline_events": [
                        {"era": "Year 0", "event": "The ancient pact was shattered."},
                        {"era": "Year 3", "event": f"{p} awakens their dormant power."}
                    ],
                    "characters": [
                        {
                            "name": p,
                            "role": "Protagonist",
                            "personality": "Determined, stoic, fiercely protective of the innocent.",
                            "appearance": ctx["protagonist_desc"],
                            "canon_data": {
                                "hair": "Dark spiky hair",
                                "eyes": "Piercing silver-amber",
                                "clothing": "Dark traveling coat with wrapped bandages",
                                "accessories": ["Guardian talisman"],
                                "visual_consistency_rules": ["Keeps talisman visible at all times."]
                            }
                        },
                        {
                            "name": s,
                            "role": "Supporting",
                            "personality": "Perceptive, loyal, master of tactical support.",
                            "appearance": ctx["supporter_desc"],
                            "canon_data": {
                                "hair": "Dark brown hair",
                                "eyes": "Keen observant eyes",
                                "clothing": "Light robes with protective leather bracers",
                                "accessories": ["Ancient scroll"],
                                "visual_consistency_rules": ["Scroll slung over shoulder."]
                            }
                        }
                    ],
                    "plot_arcs": [
                        {"title": "The Awakening", "summary": f"{p} uncovers the sealed power and escapes the ambush.", "order_index": 1},
                        {"title": "The Counter-Strike", "summary": "Assaulting the fortress to liberate the district.", "order_index": 2}
                    ]
                }

            return {
                "content": json.dumps(data, indent=2),
                "parsed_json": data,
                "model_used": "mock-manga-architect",
                "provider": "mock",
                "tokens_used": 650,
                "success": True,
                "error": None
            }

        # Handle Chapter Outline / Scenes / Panels
        if "chapter" in prompt_lower or "outline" in prompt_lower or "scene" in prompt_lower or "director" in prompt_lower or "panel" in prompt_lower:
            if theme == "nautical":
                data = {
                    "chapter_title": "Chapter 1: The Raging Tide",
                    "synopsis": f"Amidst a roaring midnight squall on the open ocean, {p} and {s} steer their sailing ship through colossal waves, facing off against an Admiralty war vessel blocking the sea corridor.",
                    "beats": [
                        f"Beat 1: Giant ocean waves batter the wooden hull as sea spray engulfs the deck.",
                        f"Beat 2: {p} grips the helm with iron determination, shouting orders through the howling storm wind.",
                        f"Beat 3: An enemy ironclad battleship breaches the tempest fog, firing grappling hooks onto the deck.",
                        f"Beat 4: {p} leaps onto the bulwark, unleashing a roaring water-dragon wave strike across the sea."
                    ],
                    "scenes": [
                        {
                            "title": "Scene 1: Starlight and Spray",
                            "summary": f"{p} and {s} battle the surging current to keep the sailing ship upright.",
                            "order_index": 1,
                            "script": {
                                "setting": "Deck of a wooden sailing ship, driving rain, towering cresting waves, tempest sky",
                                "characters_present": [p, s],
                                "actions": f"{p} steadies the helm wheel while {s} checks the compass against the crashing spray.",
                                "dialogue": [
                                    {"speaker_name": p, "text": f"Hold onto the rigging, {s}! This squall is just getting started!", "bubble_type": "speech"}
                                ]
                            }
                        },
                        {
                            "title": "Scene 2: Broadside Ambush",
                            "summary": "An Admiralty iron corvette emerges from the mist; boarding battle begins.",
                            "order_index": 2,
                            "script": {
                                "setting": "Ship deck, tangled rigging, rain-slicked timber, ironclad warship looming in the background",
                                "characters_present": [p, "Admiralty Commander"],
                                "actions": f"{p} vaults over the shattered railing with blade drawn.",
                                "dialogue": [
                                    {"speaker_name": "Admiralty Commander", "text": "Surrender your vessel to the Grand Fleet!", "bubble_type": "shout"},
                                    {"speaker_name": p, "text": "The open sea answers to no master! WAVE SPLITTER!", "bubble_type": "shout"}
                                ]
                            }
                        }
                    ],
                    "panel_scripts": [
                        {
                            "panel_number": 1,
                            "script": "Wide establishing cinematic shot: Majestic sailing ship cutting through massive stormy ocean waves under turbulent moonlit clouds.",
                            "image_prompt": "Wide dramatic manga panel, majestic sailing ship navigating towering stormy ocean waves at midnight, turbulent sea spray, dramatic moonlight breaking through thunderclouds, crisp black ink lineart, halftone screentones",
                            "dialogue": [],
                            "narration": [{"text": "Outer Reefs of the Grand Sea. Midnight.", "box_type": "caption", "x": 6.0, "y": 6.0}],
                            "sound_effects": [{"text": "ROOOAAAR", "sfx_type": "ambient", "x": 65.0, "y": 20.0, "size": "large"}]
                        },
                        {
                            "panel_number": 2,
                            "script": f"Intense close-up of {p} gripping the ship's wheel with iron resolve, ocean wind and spray whipping across face.",
                            "image_prompt": f"Intense close-up manga panel of {p}, {ctx['protagonist_desc']}, wind whipping dark brown hair, sea spray on cheeks, piercing determined eyes reflecting crashing stormy ocean waves, dynamic manga hatching",
                            "dialogue": [{"speaker_name": p, "text": f"Hold fast, {s}! We ride the crest right through the tempest!", "bubble_type": "speech", "x": 20.0, "y": 15.0}],
                            "narration": [],
                            "sound_effects": [{"text": "CREAAAK", "sfx_type": "dramatic", "x": 70.0, "y": 65.0, "size": "medium"}]
                        },
                        {
                            "panel_number": 3,
                            "script": "Dynamic diagonal action shot: Imposing armored naval enforcer landing on the wet wooden ship deck with heavy harpoon.",
                            "image_prompt": "Action manga panel, imposing armored sea enforcer wielding heavy harpoon landing on wooden ship deck, splintering deck planks, explosive sea water splashes, dynamic diagonal camera angle",
                            "dialogue": [{"speaker_name": "Enforcer", "text": "Surrender your ship to the depths!", "bubble_type": "shout", "x": 25.0, "y": 18.0}],
                            "narration": [],
                            "sound_effects": [{"text": "CRASHHH!", "sfx_type": "impact", "x": 50.0, "y": 50.0, "size": "large"}]
                        },
                        {
                            "panel_number": 4,
                            "script": f"Climactic double-wide splash panel: {p} leaps forward across the storm deck, unleashing a colossal water-dragon vortex slash.",
                            "image_prompt": f"Epic climactic manga splash panel, young hero {p} leaping forward swinging blade with explosive dragon-shaped water vortex surge, extreme ink contrast, speedlines, sea spray droplets, masterpiece manga art",
                            "dialogue": [{"speaker_name": p, "text": "OCEAN'S ROAR, STRIKE!", "bubble_type": "shout", "x": 60.0, "y": 20.0}],
                            "narration": [],
                            "sound_effects": [{"text": "WHAAAM!", "sfx_type": "impact", "x": 15.0, "y": 40.0, "size": "huge"}]
                        }
                    ]
                }
            else:
                data = {
                    "chapter_title": f"Chapter 1: The Awakening Storm",
                    "synopsis": f"{p} and {s} confront hostile forces in a midnight clash, unleashing hidden power to turn the tide of battle.",
                    "beats": [
                        f"Beat 1: Shadows gather as alarm sirens echo across the ruins.",
                        f"Beat 2: {p} clutches their weapon, standing firm before the approaching threat.",
                        f"Beat 3: Enforcer Captain breaches the outer barrier with explosive impact.",
                        f"Beat 4: {p} unleashes their signature technique, shattering the enemy line."
                    ],
                    "scenes": [
                        {
                            "title": "Scene 1: Rising Shadows",
                            "summary": f"{p} and {s} prepare for battle as danger approaches.",
                            "order_index": 1,
                            "script": {
                                "setting": "Moonlit courtyard, wind whistling through ancient stone ruins",
                                "characters_present": [p, s],
                                "actions": f"{p} steps forward while {s} provides tactical cover from the rear.",
                                "dialogue": [
                                    {"speaker_name": p, "text": "Stay behind me. I won't let them harm this sanctuary.", "bubble_type": "speech"}
                                ]
                            }
                        },
                        {
                            "title": "Scene 2: Clash of Wills",
                            "summary": "The battle erupts with overwhelming fury.",
                            "order_index": 2,
                            "script": {
                                "setting": "Courtyard entrance, shattered stone, energy crackling in the air",
                                "characters_present": [p, "Enforcer Captain"],
                                "actions": f"{p} clashes weapons with the commander in a burst of sparks.",
                                "dialogue": [
                                    {"speaker_name": "Enforcer Captain", "text": "Your resistance ends here!", "bubble_type": "shout"},
                                    {"speaker_name": p, "text": "This is only the beginning!", "bubble_type": "shout"}
                                ]
                            }
                        }
                    ],
                    "panel_scripts": [
                        {
                            "panel_number": 1,
                            "script": "Wide establishing shot of the moonlit battleground under stormy skies.",
                            "image_prompt": f"Wide dramatic manga panel, stormy moonlit sky over ruined landscape, high contrast ink lineart, crisp screentones",
                            "dialogue": [],
                            "narration": [{"text": "Midnight in the Outer Ruins.", "box_type": "caption", "x": 6.0, "y": 6.0}],
                            "sound_effects": [{"text": "ROOOAAAR", "sfx_type": "ambient", "x": 65.0, "y": 20.0, "size": "large"}]
                        },
                        {
                            "panel_number": 2,
                            "script": f"Close-up on {p}'s eyes glowing with fierce determination.",
                            "image_prompt": f"Intense close-up manga panel of {p}'s eyes, fierce determination, {ctx['protagonist_desc']}, screentone shading",
                            "dialogue": [{"speaker_name": p, "text": "I will protect this future with my life.", "bubble_type": "speech", "x": 20.0, "y": 15.0}],
                            "narration": [],
                            "sound_effects": [{"text": "THUMP", "sfx_type": "dramatic", "x": 70.0, "y": 65.0, "size": "medium"}]
                        },
                        {
                            "panel_number": 3,
                            "script": "Action panel: Heavy enforcer smashing forward with club.",
                            "image_prompt": "Action manga panel, heavily armored warrior smashing forward, splintering debris, dynamic diagonal angle",
                            "dialogue": [{"speaker_name": "Enforcer", "text": "Found you!", "bubble_type": "shout", "x": 25.0, "y": 18.0}],
                            "narration": [],
                            "sound_effects": [{"text": "BASHHH!", "sfx_type": "impact", "x": 50.0, "y": 50.0, "size": "large"}]
                        },
                        {
                            "panel_number": 4,
                            "script": f"Climactic splash panel: {p} unleashes explosive spiritual energy strike.",
                            "image_prompt": f"Epic climactic manga splash panel, {p} swinging blade with explosive celestial aura, high contrast speedlines, ink splatter, masterpiece manga art",
                            "dialogue": [{"speaker_name": p, "text": "SPIRIT BLADE, STRIKE!", "bubble_type": "shout", "x": 60.0, "y": 20.0}],
                            "narration": [],
                            "sound_effects": [{"text": "ZKKKKKK!", "sfx_type": "impact", "x": 15.0, "y": 40.0, "size": "huge"}]
                        }
                    ]
                }

            return {
                "content": json.dumps(data, indent=2),
                "parsed_json": data,
                "model_used": "mock-manga-planner",
                "provider": "mock",
                "tokens_used": 850,
                "success": True,
                "error": None
            }

        # Default fallback response
        return {
            "content": "Story beat processed successfully in studio engine.",
            "parsed_json": {"status": "ok", "message": "Processed in mock mode"},
            "model_used": "mock-general",
            "provider": "mock",
            "tokens_used": 120,
            "success": True,
            "error": None
        }

class MockImageProvider(BaseImageProvider):
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 768,
        height: int = 1024,
        art_style: str = "Traditional Manga B&W",
        canonical_descriptions: Optional[str] = None,
        genre: str = "",
    ) -> Dict[str, Any]:
        """Generate high quality, stylized manga panel image using Pillow."""
        try:
            img = Image.new("RGB", (width, height), color=(18, 20, 26))
            draw = ImageDraw.Draw(img)

            # Draw outer manga panel border
            border_margin = 24
            draw.rectangle(
                [border_margin, border_margin, width - border_margin, height - border_margin],
                outline=(245, 245, 250),
                width=6
            )

            # Inner comic background shading
            draw.rectangle(
                [border_margin + 6, border_margin + 6, width - border_margin - 6, height - border_margin - 6],
                fill=(26, 30, 42)
            )

            # Draw dynamic manga speedlines radiating from center or corner
            center_x = width // 2
            center_y = int(height * 0.45)
            line_color = (60, 68, 90) if "color" in art_style.lower() else (180, 180, 195)
            for angle_offset in range(0, 360, 12):
                import math
                rad = math.radians(angle_offset)
                x2 = center_x + int(math.cos(rad) * width)
                y2 = center_y + int(math.sin(rad) * height)
                draw.line([(center_x, center_y), (x2, y2)], fill=line_color, width=2)

            # Draw dramatic silhouette / character portrait circle
            draw.ellipse(
                [center_x - 140, center_y - 140, center_x + 140, center_y + 140],
                fill=(10, 12, 18),
                outline=(250, 250, 250),
                width=4
            )

            # Center character symbol / sword icon
            draw.line([(center_x, center_y - 110), (center_x, center_y + 100)], fill=(255, 255, 255), width=8)
            draw.line([(center_x - 45, center_y - 40), (center_x + 45, center_y - 40)], fill=(255, 255, 255), width=8)
            draw.polygon([
                (center_x, center_y - 130),
                (center_x - 12, center_y - 105),
                (center_x + 12, center_y - 105)
            ], fill=(255, 255, 255))

            # Studio watermarks / metadata badge
            draw.rectangle([border_margin + 16, height - border_margin - 90, width - border_margin - 16, height - border_margin - 16], fill=(12, 14, 20, 220))
            
            # Simple fallback font
            prompt_preview = (prompt[:60] + "...") if len(prompt) > 60 else prompt
            draw.text((border_margin + 26, height - border_margin - 80), f"AI MANGA STUDIO PANEL", fill=(139, 92, 246))
            draw.text((border_margin + 26, height - border_margin - 58), f"Style: {art_style} | Flux Schnell Mock", fill=(200, 205, 220))
            draw.text((border_margin + 26, height - border_margin - 38), f"Prompt: {prompt_preview}", fill=(150, 155, 175))

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            img_bytes = buffer.getvalue()

            return {
                "image_bytes": img_bytes,
                "mime_type": "image/jpeg",
                "width": width,
                "height": height,
                "model_used": "mock-flux-schnell",
                "provider": "mock",
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "image_bytes": None,
                "mime_type": "image/jpeg",
                "width": width,
                "height": height,
                "model_used": "mock-flux-schnell",
                "provider": "mock",
                "success": False,
                "error": str(e)
            }
