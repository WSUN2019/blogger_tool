# My Blogging Helper

A local web app for formatting and managing blog posts on Blogger.com.  
Built for **ModernSimpleLiving.com** — navy/gold theme, inline-styled HTML, Blogger-compatible output.

---

## Features

### Blog Editor (tab 1)
OAuth connection to the Blogger API — browse all posts, pull HTML, and push changes back directly.

### Utilities (tab 2)

**Single Post tools:**

| Tool | What it does |
|------|-------------|
| **Blog Formatter** | Paste plain text or markdown → choose a color theme → get fully styled Blogger-ready HTML with live preview |
| **Smart Format (AI)** | Sends your text to Google Gemini → auto-detects sections, generates KPI stats, structures lists/tables → renders formatted post |
| **Image Extractor** | Paste raw Blogger HTML → pulls out all `<a><img></a>` image blocks, strips float styles → copy back to Blogger |

**Bulk Post tools:**

| Tool | What it does |
|------|-------------|
| **Link Cleanup** | Scan all posts for a custom HTML tag (e.g. a Google Fonts `<link>`) and remove it in bulk, 25 at a time with rate-limit protection |
| **Bulk Reformat + Images** | Select up to 10 posts at a time → AI reformats each one + extracts/cleans images → pushes updated HTML back to Blogger. Shows ✅/🔄/○ icons indicating whether each post already has the current theme applied |

### About (tab 3)
App overview, feature cards, formatter syntax reference, and built-with info.

---

## Requirements

### Python version
Python 3.10 or higher.

### Python libraries

Install all dependencies with:

```bash
pip install -r requirements.txt
```

Or individually:

```bash
pip install flask beautifulsoup4 google-genai google-api-python-client google-auth-oauthlib google-auth-httplib2
```

| Package | Purpose |
|---------|---------|
| `flask` | Web server |
| `beautifulsoup4` | HTML parsing for the image extractor |
| `google-genai` | Google Gemini AI SDK (Smart Format feature) |
| `google-api-python-client` | Blogger API v3 (Blog Editor + bulk tools) |
| `google-auth-oauthlib` | OAuth2 login flow for Blogger |
| `google-auth-httplib2` | HTTP transport for Google auth |

> **Note for Linux system Python (Ubuntu/Debian):** If `pip install` warns about system packages, add `--break-system-packages`:
> ```bash
> pip install -r requirements.txt --break-system-packages
> ```

---

## Running the app

Double-click **`run_app.sh`** in your file manager (choose "Run in Terminal" when prompted), or from a terminal:

```bash
cd ~/Python/blogger_tool
python3 app.py
```

Then open **http://localhost:5000** in your browser.  
The `run_app.sh` script opens the browser automatically after a 2-second delay.

To stop the app press **Ctrl+C** in the terminal.

---

## API Key Setup — Google Gemini (Smart Format)

The Smart Format button uses **Google Gemini 2.5 Flash** to auto-structure your text, detect KPI stats, and generate sections.

**The free tier is sufficient** — no billing required.

### Step 1 — Get a free API key

1. Go to **https://aistudio.google.com**
2. Click **Get API key** → **Create API key**
3. Copy the key (starts with `AIza…`)

### Step 2 — Save the key (two options)

**Option A — In the web app:**
1. Open the **Utilities** tab → **Single** → **Blog Formatter**
2. Click the **⚙** gear icon (top right of the button row)
3. Paste your key → click **Save Key**

**Option B — Write the file directly:**
```bash
echo "AIzaYOUR_KEY_HERE" > ~/Python/blogger_tool/config/gemini_key.txt
```

The key is stored in `config/gemini_key.txt` and never leaves your machine except when calling Google's API.

### Gemini model
The active model is selected inside the app — no code editing needed.

1. Open **Utilities** → **Blog Formatter**
2. Click the **⚙** gear icon
3. Under **Model**, click any model button to switch — the choice is saved immediately to `config/gemini_model.txt`

Available models (all free tier):

| Model | Notes |
|-------|-------|
| Gemini 2.5 Flash | Default — best quality |
| Gemini 2.5 Flash Lite | Faster, lower quota usage |
| Gemini 3 Flash (preview) | Latest generation |
| Gemini 3.1 Flash Lite (preview) | Latest preview, high quota |

> If you see a **429 RESOURCE_EXHAUSTED** error, switch to a different model via the ⚙ panel — each model has its own independent daily quota.

---

## Login Credentials

The app requires a username and password to access. Credentials can be set three ways (checked in this order):

### Option A — Environment variables (recommended for deployment)

Set `APP_USERNAME` and `APP_PASSWORD` before starting the app.

**Linux / Mac (terminal):**
```bash
export APP_USERNAME=yourusername
export APP_PASSWORD=yourpassword
python3 app.py
```

**Windows (Command Prompt):**
```cmd
set APP_USERNAME=yourusername
set APP_PASSWORD=yourpassword
python app.py
```

**Windows (PowerShell):**
```powershell
$env:APP_USERNAME="yourusername"
$env:APP_PASSWORD="yourpassword"
python app.py
```

> The `export` command shown above is Linux/Mac shell syntax. On Windows use `set` (CMD) or `$env:VAR=` (PowerShell) instead.

#### Railway.app deployment

In Railway, set environment variables via the project dashboard — no shell commands needed:

1. Open your Railway project → select your service
2. Go to **Variables** tab
3. Add:
   - `APP_USERNAME` → your chosen username
   - `APP_PASSWORD` → your chosen password
   - `GEMINI_API_KEY` → your Gemini API key (optional, can also be set in-app)
   - `GEMINI_MODEL` → e.g. `gemini-2.5-flash` (optional, defaults to 2.5 Flash)
4. Railway automatically restarts the service after saving variables

---

### Option B — Config file (local use)

Create `config/auth.txt` with your credentials (this file is gitignored):

```
yourusername
yourpassword
```

Line 1 = username, Line 2 = password.

### Option C — Hardcoded fallback

If neither env vars nor `config/auth.txt` are present, the app falls back to built-in default credentials. Change these in `app.py` if needed.

---

## Optional Setup — Blog Editor (OAuth)

The Blog Editor tab lets you pull and push post HTML directly from your Blogger account.  
It requires a one-time Google Cloud setup.

### Step 1 — Create a Google Cloud project

1. Go to **https://console.cloud.google.com**
2. Create a new project (e.g. "My Blogging Helper")
3. In the search bar, find **Blogger API v3** and enable it

### Step 2 — Create OAuth credentials

1. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
2. Application type: **Web application**
3. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:5000/blogger/callback
   ```
4. Click **Create**, then **Download JSON**

### Step 3 — Save the credentials file

Rename the downloaded file to `credentials.json` and place it here:

```
blogger_tool/
└── config/
    └── credentials.json   ← put it here
```

### Step 4 — Connect in the app

1. Open the **Blog Editor** tab
2. Click **Connect with Google**
3. Authorize in the browser — you'll be redirected back automatically
4. Enter your blog URL to load posts

---

## File Structure

```
blogger_tool/
├── app.py                  # Flask web server — all routes
├── blogformat.py           # Blog post renderer (themes, sections, TOC, tables)
├── img_cleaner.py          # Image tag extractor (also works as CLI)
├── run_app.sh              # Click-to-launch script (Linux)
├── requirements.txt        # Python dependencies
├── sample.txt              # Sample post for testing the formatter
├── templates/
│   ├── index.html          # Full web app UI (3 tabs: Blog Editor, Utilities, About)
│   └── login.html          # Sign-in page
├── html_input/             # Drop HTML files here for CLI image extraction
├── html_output/            # CLI extraction results written here
└── config/
    ├── gemini_key.txt       # Your Gemini API key (gitignored)
    ├── gemini_model.txt     # Selected Gemini model (gitignored)
    ├── auth.txt             # Username/password for local use (gitignored)
    ├── credentials.json     # Google OAuth client secret (gitignored)
    └── token.json           # Stored OAuth token (gitignored, auto-created)
```

---

## Blog Formatter — Input Format

The formatter accepts plain text or light markdown. With Smart Format (AI) you can skip the syntax entirely — just paste and let Gemini structure it. For manual input:

```
TITLE: My Post Title
SUBTITLE: An optional italic subtitle
EYEBROW: Travel Journal
STATS: 13 Days | ~1,400 Miles | 4 Cities | 1 National Park

# Section Heading

Regular paragraph text here.

## Sub-label

More text under a small all-caps sub-label.

- **Item Name** — description of the item
- **Another Item** — more details

> This is a callout / tip block — styled with a gold left border.

| Column A | Column B | Column C |
|----------|----------|----------|
| value    | value    | value    |

FOOTER: Thanks for reading — ModernSimpleLiving.com
```

### Available themes

| Key | Name |
|-----|------|
| `navy_gold` | Navy / Gold (default) |
| `woodsy` | Forest Green / Amber |
| `ocean` | Deep Blue / Seafoam |
| `brick` | Rust Red / Amber |
| `purple` | Purple / Gold |
| `forest` | Deep Green / Sage |
| `slate` | Charcoal / Copper |

Each formatted post embeds a hidden `<!-- bt:{theme_key} -->` marker so the Bulk Reformat tool can detect which posts already use the current theme.

---

## Image Extractor — CLI usage

The extractor also works from the command line without the web app:

```bash
cd ~/Python/blogger_tool

# Place your HTML file in html_input/ then run:
python3 img_cleaner.py
```

Output is saved to `html_output/cleaned_images.html`.

---

## Bulk Tools — Rate Limiting

The Blogger API has a quota of ~60 requests per minute. The bulk tools automatically add a delay between posts (1.5 s for Link Cleanup, 3 s for Bulk Reformat) to stay within limits. If you have a large number of posts, expect the operation to take several minutes. Both tools show a real-time progress bar and have a **✕ Cancel** button to stop mid-run.

---

## Troubleshooting

**App won't start**
- Make sure you're in the `blogger_tool/` directory
- Run `python3 -c "import flask, bs4"` to verify packages are installed

**Smart Format button grayed out**
- Gemini key not saved yet — click ⚙ to set it up

**Gemini 429 error**
- Your key hit the free quota for the selected model
- Switch to a different model via the ⚙ panel — each model has its own independent quota

**Blog Editor — "credentials.json not found"**
- Complete the Google Cloud OAuth setup above and place the file in `config/`

**Blog Editor — OAuth error after callback**
- Make sure `http://localhost:5000/blogger/callback` is listed as an authorized redirect URI in your Google Cloud credentials

**Bulk tools — 429 rate limit error mid-run**
- Click Cancel, wait a minute, then resume from where you left off
