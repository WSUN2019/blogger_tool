# My Blogging Helper

A private local web app for writing, formatting, and managing posts on Blogger.com.  
Built with Python / Flask. Runs entirely on your machine — no data leaves except API calls to Google.

---

## Getting Started

### Requirements

Python 3.10+. Install dependencies:

```bash
pip install -r requirements.txt
```

> **Ubuntu/Debian:** add `--break-system-packages` if pip warns about system packages.

### Running

```bash
cd ~/Python/my_blogging_helper
python3 app.py
```

Open **http://localhost:5000**. Press **Ctrl+C** to stop.  
Or double-click `run_app.sh` (Linux — opens browser automatically).

### Login Credentials

Set via environment variables or a config file (in order of priority):

**Option A — env vars:**
```bash
export APP_USERNAME=yourname
export APP_PASSWORD=yourpassword
```

**Option B — `config/auth.txt`** (gitignored):
```
yourname
yourpassword
```

---

## Config Tab

Set your blog URL or numeric Blogger blog ID once here. It is used by Blog Editor, Link Cleanup, and Bulk Reformat — no need to enter it per page.

---

## Blog Editor

OAuth connection to Blogger API v3. Requires one-time setup (see below).

| Feature | What it does |
|---------|-------------|
| **Browse & Edit** | Browse posts by year, search by title, load HTML, edit, and push changes back to Blogger |
| **Reformat + Images** | One-click: AI smart-formats the post with the active theme, extracts images, appends them at the end |
| **Format with Theme** | Popup theme picker — re-renders the post HTML with a chosen color theme, in place |
| **Save Version** | Snapshots the current post HTML to `blog_backup/versions/<post_id>.atom` |
| **Version Toggle** | Switch between the live Blogger version and any saved snapshot. Badge shows live / modified / version state |

### OAuth Setup

1. **console.cloud.google.com** → create a project → enable **Blogger API v3**
2. **Credentials → Create → OAuth 2.0 Client ID** (Web application)  
   Add redirect URI: `http://localhost:5000/blogger/callback`
3. Download JSON → rename to `credentials.json` → place in `config/`
4. Open **Blog Editor** → **Connect with Google**

---

## Utilities

Accessed via the **Utilities ▾** dropdown in the nav. Three sections:

### Single Post

| Tool | What it does |
|------|-------------|
| **Blog Formatter** | Paste plain text or markdown → choose a theme → fully styled inline-CSS Blogger HTML |
| **Smart Format (AI)** | Sends text to Google Gemini → auto-structures sections, KPI stats, lists, tables |
| **Image Cleaner** | Paste Blogger HTML → extracts all `<a><img>` blocks, strips float styles |

### Bulk Operations

| Tool | What it does |
|------|-------------|
| **Link Cleanup** | Scan all posts and remove a stray HTML tag (e.g. a Google Fonts `<link>`) in bulk |
| **Bulk Reformat + Images** | AI-reformat + extract images across multiple posts, 10 at a time, pushed back to Blogger |

### Backup Posts

| Feature | What it does |
|---------|-------------|
| **Generate Backup** | Pulls all posts from Blogger API, saves as `blogname_YYYYMMDD.atom` in `blog_backup/` |
| **Browse Backups** | Switch between saved backup files, filter by year or label, preview HTML, copy to clipboard |

---

## Gemini Setup (Smart Format / Bulk Reformat)

The free tier is sufficient — no billing required.

1. Go to **https://aistudio.google.com** → **Get API key** → **Create API key**
2. Copy the key (starts with `AIza…`)
3. In the app: **Utilities → Blog Formatter → ⚙** → paste key → **Save Key**

Switch models from the same ⚙ panel. Each model has its own daily quota — if you hit a 429 error, switch to another.

| Model | Notes |
|-------|-------|
| Gemini 2.5 Flash | Default |
| Gemini 2.5 Flash Lite | Faster, lower quota usage |
| Gemini 3 Flash (preview) | Latest generation |
| Gemini 3.1 Flash Lite (preview) | Latest preview |

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

---

## File Structure

```
my_blogging_helper/
├── app.py                    # Flask server — all routes
├── blogformat.py             # Post renderer (themes, sections, tables)
├── img_cleaner.py            # Image tag extractor
├── run_app.sh                # Click-to-launch (Linux)
├── requirements.txt
├── templates/
│   ├── index.html            # Web app UI
│   └── login.html
├── blog_backup/
│   ├── blogname_YYYYMMDD.atom  # Generated backups (Utilities → Backup Posts)
│   └── versions/             # Per-post version snapshots (<post_id>.atom)
└── config/                   # All gitignored
    ├── blog_url.txt
    ├── gemini_key.txt
    ├── gemini_model.txt
    ├── auth.txt
    ├── credentials.json
    └── token.json
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Smart Format button grayed out | Gemini key not saved — click ⚙ in Blog Formatter |
| Gemini 429 error | Daily quota hit — switch model in ⚙ panel |
| `credentials.json not found` | Complete OAuth setup, place file in `config/` |
| OAuth error after callback | Confirm `http://localhost:5000/blogger/callback` is in Google Cloud redirect URIs |
| Bulk tools 429 mid-run | Cancel, wait a minute, resume |
| No posts in Backup Posts | Generate a backup first — connect Blog Editor, then use ⟳ Generate from Blogger |
