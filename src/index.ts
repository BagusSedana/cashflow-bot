import { config, validateConfig } from "./config";
import { logger } from "./utils/logger";
import { getDatabase, closeDatabase } from "./database";
import { createBot, startBot } from "./bot";
import { createAdminServer, startAdminServer } from "./admin/server";

async function main(): Promise<void> {
  logger.info("=== AI Telegram Bot Template ===");
  logger.info("Starting up...");

  // Validate configuration
  try {
    validateConfig();
  } catch (error) {
    logger.error(`Configuration error: ${error}`);
    process.exit(1);
  }

  // Initialize database
  getDatabase();
  logger.info("Database connected");

  // Start admin dashboard
  const adminApp = createAdminServer();
  startAdminServer(adminApp);

  // Start bot
  const bot = createBot();
  await startBot(bot);

  // Graceful shutdown
  const shutdown = async (): Promise<void> => {
    logger.info("Shutting down...");
    bot.stop();
    closeDatabase();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((error) => {
  logger.error(`Fatal error: ${error}`);
  process.exit(1);
});
