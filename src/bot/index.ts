import { Bot } from "grammy";
import { config } from "../config";
import { BotContext, userMiddleware, rateLimitMiddleware, errorMiddleware } from "./middleware";
import { registerCommands, registerCallbacks } from "./commands";
import { logger } from "../utils/logger";

export function createBot(): Bot<BotContext> {
  const bot = new Bot<BotContext>(config.telegram.token);

  // Register middleware
  bot.use(userMiddleware);
  bot.use(rateLimitMiddleware);

  // Register commands and callbacks
  registerCommands(bot);
  registerCallbacks(bot);

  // Error handler
  bot.catch(({ error, ctx }) => {
    errorMiddleware(error instanceof Error ? error : new Error(String(error)), ctx);
  });

  logger.info("Bot instance created with all handlers registered");
  return bot;
}

export async function startBot(bot: Bot<BotContext>): Promise<void> {
  // Set bot commands for the menu
  await bot.api.setMyCommands([
    { command: "start", description: "Start the bot" },
    { command: "help", description: "Show available commands" },
    { command: "ask", description: "Ask AI a question" },
    { command: "image", description: "Generate an image" },
    { command: "voice", description: "Convert text to speech" },
    { command: "summarize", description: "Summarize text" },
    { command: "translate", description: "Translate text" },
    { command: "code", description: "Analyze code" },
    { command: "usage", description: "View usage stats" },
    { command: "premium", description: "Premium info" },
    { command: "language", description: "Change language" },
    { command: "clear", description: "Clear chat history" },
  ]);

  logger.info("Starting bot in polling mode...");
  bot.start({
    onStart: () => { logger.info("Bot is running!"); },
  });
}
