import Database from "better-sqlite3";
import path from "path";
import fs from "fs";
import { config } from "../config";
import { logger } from "../utils/logger";

let db: Database.Database;

export function getDatabase(): Database.Database {
  if (!db) {
    const dbDir = path.dirname(config.database.path);
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
    }
    db = new Database(config.database.path);
    db.pragma("journal_mode = WAL");
    db.pragma("foreign_keys = ON");
    initializeDatabase();
  }
  return db;
}

function initializeDatabase(): void {
  logger.info("Initializing database...");

  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      telegram_id INTEGER UNIQUE NOT NULL,
      username TEXT,
      first_name TEXT,
      last_name TEXT,
      language TEXT DEFAULT 'en',
      is_premium INTEGER DEFAULT 0,
      premium_expires_at TEXT,
      total_requests INTEGER DEFAULT 0,
      daily_requests INTEGER DEFAULT 0,
      last_request_date TEXT,
      is_banned INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS conversations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      tokens_used INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(telegram_id)
    );

    CREATE TABLE IF NOT EXISTS usage_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      feature TEXT NOT NULL,
      tokens_used INTEGER DEFAULT 0,
      cost_estimate REAL DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(telegram_id)
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);
  `);

  logger.info("Database initialized successfully");
}

export function closeDatabase(): void {
  if (db) {
    db.close();
    logger.info("Database connection closed");
  }
}
