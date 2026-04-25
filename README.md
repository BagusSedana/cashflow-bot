# 🤖 AI Telegram Bot Template

A **production-ready**, feature-rich AI Telegram Bot template powered by **OpenAI (ChatGPT, DALL-E, TTS)**. Built with TypeScript, includes an admin dashboard, user management, subscription system, and multi-language support.

**Perfect for selling on CodeCanyon, Gumroad, or building your own AI bot SaaS.**

![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 🧠 AI Features (Powered by OpenAI)
- **💬 ChatGPT** — Conversational AI with context memory
- **🎨 Image Generation** — Create images from text descriptions (DALL-E 3)
- **🔊 Text-to-Speech** — Convert text to natural speech (6 voices)
- **📝 Summarize** — Summarize long texts instantly
- **🌐 Translate** — Translate between any languages
- **💻 Code Analysis** — Analyze and explain code snippets

### 👥 User Management
- Automatic user registration
- Daily request limits (configurable)
- Premium subscription system
- Ban/unban users

### 📊 Admin Dashboard
- Beautiful web-based dashboard
- Real-time statistics
- User management (ban, premium, etc.)
- Usage analytics by feature
- Token & cost tracking

### 🌍 Multi-Language
- English and Bahasa Indonesia included
- Easy to add more languages

### 🚀 Production Ready
- TypeScript for type safety
- SQLite database (zero config)
- Rate limiting
- Error handling & logging
- Docker support
- Graceful shutdown

---

## 📋 Quick Start

### Prerequisites
- **Node.js 18+** ([Download](https://nodejs.org))
- **Telegram Bot Token** ([Get from @BotFather](https://t.me/BotFather))
- **OpenAI API Key** ([Get from OpenAI](https://platform.openai.com/api-keys))

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/ai-telegram-bot.git
cd ai-telegram-bot
npm install
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### 3. Run

```bash
# Development (with hot reload)
npm run dev

# Production
npm run build
npm start
```

### 4. Open Admin Dashboard

Visit `http://localhost:3000` and login with your admin credentials.

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/ask <question>` | Ask AI anything |
| `/image <description>` | Generate an image |
| `/voice <text>` | Convert text to speech |
| `/summarize <text>` | Summarize text |
| `/translate <lang> <text>` | Translate text |
| `/code <code>` | Analyze code |
| `/usage` | View your stats |
| `/premium` | Premium info |
| `/language` | Change language |
| `/clear` | Clear chat history |

You can also **send any text message** directly and the bot will respond as a chatbot.

---

## 🏗️ Project Structure

```
ai-telegram-bot/
├── src/
│   ├── index.ts              # Entry point
│   ├── config.ts             # Configuration
│   ├── ai/
│   │   └── openai.ts         # OpenAI integration (Chat, Image, TTS)
│   ├── bot/
│   │   ├── index.ts          # Bot setup
│   │   ├── commands.ts       # Command handlers
│   │   └── middleware.ts     # Auth, rate limit, usage tracking
│   ├── database/
│   │   ├── index.ts          # SQLite setup & migrations
│   │   ├── users.ts          # User CRUD operations
│   │   ├── conversations.ts  # Chat history
│   │   └── usage.ts          # Usage logging & analytics
│   ├── admin/
│   │   └── server.ts         # Express admin API
│   ├── i18n/
│   │   ├── index.ts          # Translation engine
│   │   ├── en.ts             # English translations
│   │   └── id.ts             # Indonesian translations
│   └── utils/
│       └── logger.ts         # Winston logger
├── admin/                    # Admin dashboard (static files)
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── package.json
└── tsconfig.json
```

---

## ⚙️ Configuration

All settings are in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | *required* |
| `OPENAI_API_KEY` | OpenAI API key | *required* |
| `OPENAI_CHAT_MODEL` | Chat model | `gpt-4o-mini` |
| `OPENAI_IMAGE_MODEL` | Image model | `dall-e-3` |
| `OPENAI_TTS_MODEL` | TTS model | `tts-1` |
| `OPENAI_TTS_VOICE` | TTS voice | `alloy` |
| `DATABASE_PATH` | SQLite database path | `./data/bot.db` |
| `ADMIN_PORT` | Admin dashboard port | `3000` |
| `ADMIN_USERNAME` | Admin login username | `admin` |
| `ADMIN_PASSWORD` | Admin login password | `changeme123` |
| `BOT_DEFAULT_LANGUAGE` | Default language | `en` |
| `BOT_MAX_FREE_REQUESTS` | Free daily limit | `20` |
| `BOT_PREMIUM_PRICE` | Premium price display | `5.00` |
| `RATE_LIMIT_WINDOW_MS` | Rate limit window | `60000` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per window | `10` |
| `LOG_LEVEL` | Logging level | `info` |

---

## 🌍 Adding a New Language

1. Create a new file in `src/i18n/` (e.g., `es.ts`)
2. Copy the structure from `en.ts` and translate
3. Add the import in `src/i18n/index.ts`
4. Add the language to `getSupportedLanguages()`

---

## 💰 Monetization Ideas

- **Freemium Model** — Free tier with daily limits, premium for unlimited
- **Sell the Template** — List on CodeCanyon ($29-49), Gumroad, or Shopee
- **White Label** — Customize and sell to businesses
- **SaaS** — Host and charge monthly subscriptions

---

## 🔧 OpenAI Cost Estimates

| Feature | Model | Approx. Cost |
|---------|-------|-------------|
| Chat | gpt-4o-mini | ~$0.0001/message |
| Image | dall-e-3 | ~$0.04/image |
| TTS | tts-1 | ~$0.015/1K chars |
| Summarize | gpt-4o-mini | ~$0.0002/request |
| Translate | gpt-4o-mini | ~$0.0001/request |
| Code | gpt-4o-mini | ~$0.0002/request |

---

## 📄 License

MIT License — free for personal and commercial use.

---

## 🤝 Support

- Open an issue on GitHub
- Email: gedebagussedanayoga28@gmail.com

---

Built with ❤️ by [BagusSedana](https://github.com/BagusSedana)
