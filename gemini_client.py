"""Shared Gemini API helpers."""
import os
from config import GEMINI_KEY_FILE, GEMINI_MODEL_FILE

GEMINI_MODELS = [
    {'id': 'gemini-2.5-flash',              'label': 'Gemini 2.5 Flash'},
    {'id': 'gemini-2.5-flash-lite-preview', 'label': 'Gemini 2.5 Flash Lite'},
    {'id': 'gemini-3-flash-preview',        'label': 'Gemini 3 Flash'},
    {'id': 'gemini-3.1-flash-lite-preview', 'label': 'Gemini 3.1 Flash Lite'},
]
DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash'

GEMINI_PROMPT = """\
You are a blog formatter for a lifestyle blog covering travel, food, gear, and everyday living.

Convert the user's raw text into structured markdown that a blog formatter will render into styled HTML.

OUTPUT FORMAT (follow exactly, no code fences, no explanation):

TITLE: The post title
SUBTITLE: One-line italic subtitle (skip if nothing natural fits)
EYEBROW: Short category label — pick best: Travel Journal, Wine Review, Gear Review, Food & Drink, Road Trip, City Guide, Feature
STATS: value1 Label1 | value2 Label2 | value3 Label3

# Section Heading

Paragraph text here.

## Sub-label

More paragraph text.

- **Item Name** — description
- **Another** — description

> Tip or callout text — italic highlighted block

| Col A | Col B | Col C |
|-------|-------|-------|
| val   | val   | val   |

FOOTER: Closing line

RULES:
- STATS: extract or intelligently estimate 3–5 KPI numbers from the content.
  Examples: Days, Nights, Miles, Cities, Stops, Items, Bottles, Price, Hours, etc.
  Use ~ prefix for approximations (e.g. "~1,400").
- Create logical # sections. Posts with 3+ sections auto-get a table of contents.
- Use ## sub-labels for time periods (Morning, Evening), categories, or sub-topics.
- Convert enumerated items, gear lists, or steps to - bullet format with **Bold Name** — desc.
- Convert comparison or tabular data to markdown tables.
- Wrap tips, notes, key advice, or quotes in > callout blocks.
- Preserve ALL original content — restructure, never summarize or drop details.
- Section eyebrows can include context: e.g. "Section II — Day 1" as the LABEL.

User's text:
"""


def _get_gemini_key() -> str:
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    if key:
        return key
    if os.path.exists(GEMINI_KEY_FILE):
        with open(GEMINI_KEY_FILE) as f:
            return f.read().strip()
    return ''


def _get_gemini_model() -> str:
    val = os.environ.get('GEMINI_MODEL', '').strip()
    if val:
        return val
    if os.path.exists(GEMINI_MODEL_FILE):
        val = open(GEMINI_MODEL_FILE).read().strip()
        if val:
            return val
    return DEFAULT_GEMINI_MODEL
