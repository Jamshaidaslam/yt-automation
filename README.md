# 🤖 AI Dark Realities — Automated Short-Form Video Pipeline

A fully automated, **100% free** system that creates and posts 3 viral vertical
short-form videos per day across YouTube Shorts, Instagram Reels, Facebook Reels,
and Snapchat Spotlight — running entirely via **GitHub Actions**.

---

## 🗂 File Structure

```
.
├── .github/
│   └── workflows/
│       └── video_pipeline.yml   ← GitHub Actions cron automation
├── fonts/
│   └── Montserrat-ExtraBold.ttf ← Drop your font here (auto-downloaded in CI)
├── output/
│   ├── audio/                   ← TTS .mp3 files + word-timing JSON sidecars
│   ├── scripts/                 ← Groq-generated script + SEO JSON files
│   ├── media/                   ← Downloaded B-roll clips (auto-cleaned in CI)
│   └── final_videos/            ← Rendered MP4s + Snapchat metadata
├── config.py                    ← All settings (API keys, dimensions, fonts)
├── script_generator.py          ← Groq LLM script + SEO generation
├── media_fetcher.py             ← Pexels/Pixabay downloader with fallback
├── audio_generator.py           ← Edge-TTS voiceover + word-timing extraction
├── video_compiler.py            ← FFmpeg/MoviePy render engine
├── uploader.py                  ← YouTube + Meta multi-platform posting
├── main.py                      ← End-to-end pipeline orchestrator
└── requirements.txt
```

---

## ⚡ Quick Start (Local)

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/ai-dark-reels.git
cd ai-dark-reels
pip install -r requirements.txt
sudo apt-get install -y ffmpeg imagemagick   # Ubuntu/Debian
```

### 2. Add your font
```bash
# Download Montserrat ExtraBold (free Google Font)
wget -O fonts/Montserrat-ExtraBold.ttf \
  "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-ExtraBold.ttf"
```

### 3. Set environment variables
Create a `.env` file (never commit this):
```env
GROQ_API_KEY=gsk_...
PEXELS_API_KEY=...
PIXABAY_API_KEY=...
YOUTUBE_CLIENT_SECRET={"installed":{...}}   # Full JSON string
YOUTUBE_TOKEN_JSON={"token":"..."}          # After first OAuth run
META_ACCESS_TOKEN=EAAx...
INSTAGRAM_ACCOUNT_ID=12345678
FACEBOOK_PAGE_ID=87654321
```

### 4. Run a test (render only, no upload)
```bash
python main.py --skip-upload
# Or force a topic:
python main.py --topic "How AI reads your emotions without asking" --skip-upload
```

---

## 🔐 GitHub Secrets Setup

Go to **Settings → Secrets and variables → Actions** in your repo and add:

| Secret name | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api/) |
| `PIXABAY_API_KEY` | [pixabay.com/api/docs](https://pixabay.com/api/docs/) |
| `YOUTUBE_CLIENT_SECRET` | [Google Cloud Console](https://console.cloud.google.com) → OAuth 2.0 Client → Download JSON → paste as string |
| `YOUTUBE_TOKEN_JSON` | Run `python main.py --skip-upload` locally first; copy printed token JSON |
| `META_ACCESS_TOKEN` | [Meta Business Manager](https://business.facebook.com) → Long-Lived Page Token |
| `INSTAGRAM_ACCOUNT_ID` | Meta Graph API Explorer: `GET /me/accounts` |
| `FACEBOOK_PAGE_ID` | Same as above |

---

## 🎬 YouTube OAuth2 First-Run

YouTube requires a one-time browser authorisation. Run this locally **before**
pushing to GitHub:

```bash
python -c "import uploader; uploader._get_youtube_service()"
```

Follow the browser prompt, then copy the printed token JSON into the
`YOUTUBE_TOKEN_JSON` GitHub Secret.

---

## ⏰ Cron Schedule

| Cron (UTC) | EST | GMT | Slot |
|---|---|---|---|
| `0 11 * * *` | 7:00 AM | 12:00 PM | Morning |
| `0 17 * * *` | 1:00 PM | 6:00 PM | Afternoon |
| `0 23 * * *` | 7:00 PM | 12:00 AM | Prime Time |

---

## 🎨 Customisation

| Setting | File | Variable |
|---|---|---|
| Caption colour | `config.py` | `CAPTION_ACTIVE_COLOR` |
| TTS voice | `config.py` | `TTS_VOICE` |
| Video resolution | `config.py` | `VIDEO_WIDTH / VIDEO_HEIGHT` |
| Clip cut speed | `config.py` | `CLIP_MIN_SEC / CLIP_MAX_SEC` |
| Topic pool | `script_generator.py` | `TOPIC_POOL` list |

---

## 📜 Licence
MIT — free to use, modify, and deploy.
