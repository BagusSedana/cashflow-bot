import dotenv from "dotenv";
import path from "path";

dotenv.config();

export const config = {
  telegram: {
    token: process.env.TELEGRAM_BOT_TOKEN || "",
  },
  openai: {
    apiKey: process.env.OPENAI_API_KEY || "",
    chatModel: process.env.OPENAI_CHAT_MODEL || "gpt-4o-mini",
    imageModel: process.env.OPENAI_IMAGE_MODEL || "dall-e-3",
    ttsModel: process.env.OPENAI_TTS_MODEL || "tts-1",
    ttsVoice: (process.env.OPENAI_TTS_VOICE || "alloy") as
      | "alloy"
      | "echo"
      | "fable"
      | "onyx"
      | "nova"
      | "shimmer",
  },
  database: {
    path: process.env.DATABASE_PATH || path.join(process.cwd(), "data", "bot.db"),
  },
  admin: {
    port: parseInt(process.env.ADMIN_PORT || "3000", 10),
    username: process.env.ADMIN_USERNAME || "admin",
    password: process.env.ADMIN_PASSWORD || "changeme123",
  },
  bot: {
    defaultLanguage: process.env.BOT_DEFAULT_LANGUAGE || "en",
    maxFreeRequests: parseInt(process.env.BOT_MAX_FREE_REQUESTS || "20", 10),
    premiumPrice: parseFloat(process.env.BOT_PREMIUM_PRICE || "5.00"),
  },
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || "60000", 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || "10", 10),
  },
  logging: {
    level: process.env.LOG_LEVEL || "info",
  },
};

export function validateConfig(): void {
  if (!config.telegram.token) {
    throw new Error("TELEGRAM_BOT_TOKEN is required. Get one from @BotFather on Telegram.");
  }
  if (!config.openai.apiKey) {
    throw new Error("OPENAI_API_KEY is required. Get one from https://platform.openai.com/api-keys");
  }
}
