from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    key: str
    name: str
    primary: str
    accent: str
    accent_light: str
    bg: str
    warm: str
    border: str
    muted: str
    body_text: str


THEMES: dict[str, Theme] = {
    "navy_gold": Theme(
        key="navy_gold", name="Navy / Gold (default)",
        primary="#1a2640", accent="#c9a84c", accent_light="#e8d5a3",
        bg="#faf8f4", warm="#f2ede4", border="#d9cfc0",
        muted="#6b7280", body_text="#3a3a3a",
    ),
    "woodsy": Theme(
        key="woodsy", name="Woodsy (forest green / amber)",
        primary="#2d3f2e", accent="#b8893a", accent_light="#e4c78a",
        bg="#f8f5ef", warm="#ece5d6", border="#d4c9b3",
        muted="#6b6257", body_text="#3a3a3a",
    ),
    "ocean": Theme(
        key="ocean", name="Ocean (deep blue / seafoam)",
        primary="#12304a", accent="#3a9ea5", accent_light="#a8d8db",
        bg="#f5f8fa", warm="#e4edf1", border="#c8d4dc",
        muted="#5c6b75", body_text="#2f3a42",
    ),
    "brick": Theme(
        key="brick", name="Brick (rust red / amber)",
        primary="#6e2b1f", accent="#d4892a", accent_light="#f0c88a",
        bg="#faf6f0", warm="#f0e6d6", border="#dac8b0",
        muted="#6f6254", body_text="#3a2f2a",
    ),
    "purple": Theme(
        key="purple", name="Purple / Gold",
        primary="#3d2c5e", accent="#c9a84c", accent_light="#e8d5a3",
        bg="#f8f5fa", warm="#ece4f0", border="#d4c6df",
        muted="#6b6275", body_text="#3a3340",
    ),
    "forest": Theme(
        key="forest", name="Forest (deep green / sage)",
        primary="#1f3d2f", accent="#7a9b5c", accent_light="#c4d6b0",
        bg="#f6f8f3", warm="#e4ebdc", border="#c9d3bf",
        muted="#606a5c", body_text="#2f3a34",
    ),
    "slate": Theme(
        key="slate", name="Slate (charcoal / copper)",
        primary="#2b2f36", accent="#c87a4a", accent_light="#edc3a3",
        bg="#f6f5f2", warm="#e7e4dd", border="#cdc8bd",
        muted="#6a6862", body_text="#353434",
    ),
}
