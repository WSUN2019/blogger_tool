# My Blogging Helper

A private local web app for writing, formatting, and managing posts on Blogger.com.  
Built with Python / Flask. Runs entirely on your machine — no data leaves except API calls to Google.

---

## Tabs

### Blog Editor
OAuth connection to Blogger API v3. Browse posts by year, load HTML, reformat with AI + images, save local version snapshots, and push changes back live.

### Utilities

**Single Post:**

| Tool | What it does |
|------|-------------|
| **Blog Formatter** | Plain text or markdown → choose a theme → fully styled inline-CSS Blogger HTML |
| **Smart Format (AI)** | Sends text to Google Gemini → auto-structures sections, KPI stats, lists, tables |
| **Image Extractor** | Paste Blogger HTML → extracts all `<a><img>` blocks, strips float styles |

**Bulk:**

| Tool | What it does |
|------|-------------|
| **Link Cleanup** | Remove a stray HTML tag (e.g. a Google Fonts `<link>`) from every post in bulk |
| **Bulk Reformat + Images** | Select posts → AI reformats + extracts images → pushes back up to 10 at a time |

### Backup Reviewer
Upload your `feed.atom` Blogger export (Settings → Back up content) to `blog_backup/`. Browse all posts, filter by year or label, preview HTML, copy to clipboard.

### Post Versions (within Blog Editor)
Click **💾 Save Version** on any open post to snapshot its HTML as an Atom entry in `blog_backup/versions/<post_id>.atom`. A versions panel shows all saved snapshots alongside the current live version — toggle between them with one click.

---

## Requirements

Python 3.10+. Install dependencies:

```bash
pip install -r requirements.txt
```

> **Ubuntu/Debian system Python:** add `--break-system-packages` if pip warns about system packages.

---

## Running

```bash
cd ~/Python/my_blogging_helper
python3 app.py
```

Then open **http://localhost:5000**.  
Or double-click `run_app.sh` (Linux — opens browser automatically).

Press **Ctrl+C** to stop.

---

## Setup — Google Gemini (Smart Format)

The free tier is sufficient — no billing required.

1. Go to **https://aistudio.google.com** → **Get API key** → **Create API key**
2. Copy the key (starts with `AIza…`)
3. In the app: **Utilities → Blog Formatter → ⚙** → paste key → **Save Key**

Switch models from the same ⚙ panel. Each model has its own independent daily quota — if you hit a 429 error, switch to another.

| Model | Notes |
|-------|-------|
| Gemini 2.5 Flash | Default |
| Gemini 2.5 Flash Lite | Faster, lower quota usage |
| Gemini 3 Flash (preview) | Latest generation |
| Gemini 3.1 Flash Lite (preview) | Latest preview |

---

## Setup — Blog Editor (OAuth)

One-time setup to connect to your Blogger account.

1. **console.cloud.google.com** → create a project → enable **Blogger API v3**
2. **Credentials → Create → OAuth 2.0 Client ID** (Web application)  
   Add redirect URI: `http://localhost:5000/blogger/callback`
3. Download JSON → rename to `credentials.json` → place in `config/`
4. Open **Blog Editor** tab → **Connect with Google**

---

## Login Credentials

Set via environment variables, a config file, or the hardcoded fallback (in order):

**Option A — env vars:**
```bash
export APP_USERNAME=yourname
export APP_PASSWORD=yourpassword
```

**Option B — config file** (`config/auth.txt`, gitignored):
```
yourname
yourpassword
```

---

## File Structure

```
my_blogging_helper/
├── app.py                  # Flask server — all routes
├── blogformat.py           # Post renderer (themes, sections, TOC, tables)
├── img_cleaner.py          # Image tag extractor
├── run_app.sh              # Click-to-launch (Linux)
├── requirements.txt
├── sample.txt
├── templates/
│   ├── index.html          # Web app UI
│   └── login.html
├── blog_backup/
│   ├── feed.atom           # Blogger export (upload via Backup Reviewer)
│   └── versions/           # Per-post version snapshots (<post_id>.atom)
├── html_input/             # CLI image extraction input
├── html_output/            # CLI image extraction output
└── config/                 # All gitignored
    ├── gemini_key.txt
    ├── gemini_model.txt
    ├── auth.txt
    ├── credentials.json
    └── token.json
```

---

## Blog Formatter — Input Syntax

```
TITLE: My Post Title
SUBTITLE: Optional italic subtitle
EYEBROW: Travel Journal
STATS: 13 Days | ~1,400 Miles | 4 Cities

# Section Heading
## Sub-label

Paragraph text.

- **Item** — description

> Callout / tip block

| Col A | Col B |
|-------|-------|
| val   | val   |

FOOTER: Thanks for reading.
```

**Themes:** `navy_gold` (default), `woodsy`, `ocean`, `brick`, `purple`, `forest`, `slate`

Each post embeds a `<!-- bt:{theme_key} -->` marker so the Bulk Reformat tool can detect which posts already use the current theme.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Smart Format button grayed out | Gemini key not saved — click ⚙ |
| Gemini 429 error | Daily quota hit — switch model in ⚙ panel |
| `credentials.json not found` | Complete OAuth setup, place file in `config/` |
| OAuth error after callback | Confirm `http://localhost:5000/blogger/callback` is in your Google Cloud redirect URIs |
| Bulk tools 429 mid-run | Cancel, wait a minute, resume |
