# EthiopicBibleAPI

A FastAPI-based REST API and Telegram bot for accessing the Ethiopian Bible (Ge'ez canon) in Amharic. Serves all 66 books with in-memory caching for fast responses.

## Features

- **REST API** — retrieve books, chapters, and individual verses
- **Telegram Bot** — get random verses, daily verses, browse books, and subscribe to scheduled morning/evening deliveries
- **In-Memory Cache** — all 66 books (~5.6 MB) loaded at startup, zero disk I/O per request
- **GZip Compression** — large responses compressed automatically
- **CORS Enabled** — any frontend can consume the API
- **Keep-Alive Ping** — self-pings `/health` every 10 minutes to prevent Render free tier from sleeping
- **Dockerized** — single image, configurable via `MODE` env var

## Project Structure

```
EthiopicBibleAPI/
├── main.py              # FastAPI application (API endpoints)
├── bot.py               # Telegram bot (commands + scheduled jobs)
├── bible_data.py        # Shared data layer (loads & queries Bible JSON)
├── schemas.py           # Pydantic response models
├── Books/               # 66 JSON files (one per Bible book, Amharic)
├── Dockerfile           # Container image
├── docker-compose.yml   # Local dev (API + bot as separate services)
├── render.yaml          # Render deployment blueprint
├── start.sh             # Entrypoint script (runs api, bot, or both)
├── requirements.txt     # Python dependencies
└── subscribers.txt      # Auto-generated subscriber list (gitignored)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/book/{book_name}` | Retrieve an entire book |
| `GET` | `/book/{book_name}/chapter/{chapter_number}` | Retrieve a specific chapter |
| `GET` | `/book/{book_name}/chapter/{chapter_number}/verse/{verse_number}` | Retrieve a single verse |

### Example Requests

```bash
# Get Genesis (ኦሪት ዘፍጥረት)
curl "http://localhost:8000/book/ኦሪት%20ዘፍጥረት"

# Get Genesis chapter 1
curl "http://localhost:8000/book/ኦሪት%20ዘፍጥረት/chapter/1"

# Get Genesis 1:1
curl "http://localhost:8000/book/ኦሪት%20ዘፍጥረት/chapter/1/verse/1"

# Health check
curl "http://localhost:8000/health"
```

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with all commands |
| `/verse` | Get a random verse from any book |
| `/daily` | Get today's verse (same all day, changes daily) |
| `/books` | Browse all 66 books with inline buttons |
| `/subscribe` | Receive automatic morning (6 AM UTC) & evening (8 PM UTC) verses |
| `/unsubscribe` | Stop receiving scheduled verses |
| `/help` | Show available commands |

## Setup

### Prerequisites

- Python 3.9+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Local Development

```bash
# Clone the repo
git clone https://github.com/natnael-wondwoesn/EthiopicBibleAPI.git
cd EthiopicBibleAPI

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload
# Visit http://127.0.0.1:8000/docs

# Run the Telegram bot (in a separate terminal)
export TELEGRAM_BOT_TOKEN="your-token-here"
python bot.py
```

### Docker

```bash
# Build the image
docker build -t ethiopic-bible .

# Run API only
docker run -p 8000:8000 -e MODE=api ethiopic-bible

# Run bot only
docker run -e MODE=bot -e TELEGRAM_BOT_TOKEN="your-token" ethiopic-bible

# Run both (API + bot in one container)
docker run -p 8000:8000 -e MODE=both -e TELEGRAM_BOT_TOKEN="your-token" ethiopic-bible

# Or use docker-compose for local dev
export TELEGRAM_BOT_TOKEN="your-token"
docker compose up --build
```

### Deploy to Render (Free)

**Option A — Blueprint (automatic):**
1. Push your repo to GitHub
2. Go to [Render](https://render.com) → **New** → **Blueprint**
3. Connect your repo — Render reads `render.yaml` and creates the service
4. Set `TELEGRAM_BOT_TOKEN` in the environment variables on the Render dashboard

**Option B — Manual:**
1. **New** → **Web Service** → connect your repo
2. Set **Runtime** to Docker, **Plan** to Free
3. Add environment variables:
   - `MODE` = `both`
   - `TELEGRAM_BOT_TOKEN` = your token
4. Deploy

The keep-alive ping activates automatically on Render (it detects `RENDER_EXTERNAL_URL`) and pings `/health` every 10 minutes to prevent the free tier from sleeping.

## Available Books (66)

<details>
<summary>Click to expand full book list</summary>

**Old Testament:**
ኦሪት ዘፍጥረት, ኦሪት ዘጸአት, ኦሪት ዘሌዋውያን, ኦሪት ዘኍልቍ, ኦሪት ዘዳግም,
መጽሐፈ ኢያሱ ወልደ ነዌ, መጽሐፈ መሣፍንት, መጽሐፈ ሩት,
መጽሐፈ ሳሙኤል ቀዳማዊ, መጽሐፈ ሳሙኤል ካል,
መጽሐፈ ነገሥት ቀዳማዊ, መጽሐፈ ነገሥት ካልዕ,
መጽሐፈ ዜና መዋዕል ቀዳማዊ, መጽሐፈ ዜና መዋዕል ካልዕ,
መጽሐፈ ዕዝራ, መጽሐፈ ነህምያ, መጽሐፈ አስቴር, መጽሐፈ ኢዮብ,
መዝሙረ ዳዊት, መጽሐፈ ምሳሌ, መጽሐፈ መክብብ, መኃልየ መኃልይ ዘሰሎሞን,
ትንቢተ ኢሳይያስ, ትንቢተ ኤርምያስ, ሰቆቃው ኤርምያስ,
ትንቢተ ሕዝቅኤል, ትንቢተ ዳንኤል, ትንቢተ ሆሴዕ, ትንቢተ ኢዮኤል,
ትንቢተ አሞጽ, ትንቢተ አብድዩ, ትንቢተ ዮናስ, ትንቢተ ሚክያስ,
ትንቢተ ናሆም, ትንቢተ ዕንባቆም, ትንቢተ ሶፎንያስ,
ትንቢተ ሐጌ, ትንቢተ ዘካርያስ, ትንቢተ ሚልክያ

**New Testament:**
የማቴዎስ ወንጌል, የማርቆስ ወንጌል, የሉቃስ ወንጌል, የዮሐንስ ወንጌል,
የሐዋርያት ሥራ, ወደ ሮሜ ሰዎች,
1ኛ ወደ ቆሮንቶስ ሰዎች, 2ኛ ወደ ቆሮንቶስ ሰዎች,
ወደ ገላትያ ሰዎች, ወደ ኤፌሶን ሰዎች, ወደ ፊልጵስዩስ ሰዎች, ወደ ቆላስይስ ሰዎች,
1ኛ ወደ ተሰሎንቄ ሰዎች, 2ኛ ወደ ተሰሎንቄ ሰዎች,
1ኛ ወደ ጢሞቴዎስ, 2ኛ ወደ ጢሞቴዎስ,
ወደ ቲቶ, ወደ ፊልሞና, ወደ ዕብራውያን,
የያዕቆብ መልእክት,
1ኛ የጴጥሮስ መልእክት, 2ኛ የጴጥሮስ መልእክት,
1ኛ የዮሐንስ መልእክት, 2ኛ የዮሐንስ መልእክት, 3ኛ የዮሐንስ መልእክት,
የይሁዳ መልእክት, የዮሐንስ ራእይ

</details>

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — async web framework
- **[python-telegram-bot](https://python-telegram-bot.org/)** — Telegram Bot API wrapper
- **[Pydantic](https://docs.pydantic.dev/)** — data validation & response models
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server
- **[Docker](https://www.docker.com/)** — containerization

## Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Container               │
│                                             │
│  ┌─────────────┐     ┌──────────────────┐   │
│  │  FastAPI     │     │  Telegram Bot    │   │
│  │  (main.py)  │     │  (bot.py)        │   │
│  │             │     │                  │   │
│  │  /health    │◄────│  keep-alive ping │   │
│  │  /book/...  │     │  /verse, /daily  │   │
│  │  /chapter/..│     │  /books, /sub    │   │
│  └──────┬──────┘     └────────┬─────────┘   │
│         │                     │             │
│         └──────────┬──────────┘             │
│                    │                        │
│           ┌────────▼────────┐               │
│           │  bible_data.py  │               │
│           │  (in-memory     │               │
│           │   cache)        │               │
│           └────────┬────────┘               │
│                    │                        │
│           ┌────────▼────────┐               │
│           │   Books/*.json  │               │
│           │   (66 files)    │               │
│           └─────────────────┘               │
└─────────────────────────────────────────────┘
```

## Original Author

- **Daniel Demerw** — [LinkedIn](https://www.linkedin.com/in/danieldemerw)
- [Original blog post](https://medium.com/@danielendale/building-ethiopicbibleapi-a-fastapi-powered-restful-api-for-the-ethiopian-bible-abfab6abfe0d)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
