import { getDatabase } from "./index";

export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language: string;
  is_premium: number;
  premium_expires_at: string | null;
  total_requests: number;
  daily_requests: number;
  last_request_date: string | null;
  is_banned: number;
  created_at: string;
  updated_at: string;
}

export function findOrCreateUser(
  telegramId: number,
  username?: string,
  firstName?: string,
  lastName?: string
): User {
  const db = getDatabase();

  const existing = db
    .prepare("SELECT * FROM users WHERE telegram_id = ?")
    .get(telegramId) as User | undefined;

  if (existing) {
    db.prepare(
      "UPDATE users SET username = ?, first_name = ?, last_name = ?, updated_at = datetime('now') WHERE telegram_id = ?"
    ).run(username || null, firstName || null, lastName || null, telegramId);
    return db.prepare("SELECT * FROM users WHERE telegram_id = ?").get(telegramId) as User;
  }

  db.prepare(
    "INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (?, ?, ?, ?)"
  ).run(telegramId, username || null, firstName || null, lastName || null);

  return db.prepare("SELECT * FROM users WHERE telegram_id = ?").get(telegramId) as User;
}

export function getUser(telegramId: number): User | undefined {
  const db = getDatabase();
  return db.prepare("SELECT * FROM users WHERE telegram_id = ?").get(telegramId) as User | undefined;
}

export function updateUserLanguage(telegramId: number, language: string): void {
  const db = getDatabase();
  db.prepare("UPDATE users SET language = ?, updated_at = datetime('now') WHERE telegram_id = ?").run(
    language,
    telegramId
  );
}

export function setUserPremium(telegramId: number, expiresAt: string): void {
  const db = getDatabase();
  db.prepare(
    "UPDATE users SET is_premium = 1, premium_expires_at = ?, updated_at = datetime('now') WHERE telegram_id = ?"
  ).run(expiresAt, telegramId);
}

export function removeUserPremium(telegramId: number): void {
  const db = getDatabase();
  db.prepare(
    "UPDATE users SET is_premium = 0, premium_expires_at = NULL, updated_at = datetime('now') WHERE telegram_id = ?"
  ).run(telegramId);
}

export function banUser(telegramId: number): void {
  const db = getDatabase();
  db.prepare("UPDATE users SET is_banned = 1, updated_at = datetime('now') WHERE telegram_id = ?").run(
    telegramId
  );
}

export function unbanUser(telegramId: number): void {
  const db = getDatabase();
  db.prepare("UPDATE users SET is_banned = 0, updated_at = datetime('now') WHERE telegram_id = ?").run(
    telegramId
  );
}

export function incrementUserRequests(telegramId: number): void {
  const db = getDatabase();
  const today = new Date().toISOString().split("T")[0];
  const user = getUser(telegramId);

  if (user && user.last_request_date !== today) {
    db.prepare(
      "UPDATE users SET total_requests = total_requests + 1, daily_requests = 1, last_request_date = ?, updated_at = datetime('now') WHERE telegram_id = ?"
    ).run(today, telegramId);
  } else {
    db.prepare(
      "UPDATE users SET total_requests = total_requests + 1, daily_requests = daily_requests + 1, last_request_date = ?, updated_at = datetime('now') WHERE telegram_id = ?"
    ).run(today, telegramId);
  }
}

export function getAllUsers(): User[] {
  const db = getDatabase();
  return db.prepare("SELECT * FROM users ORDER BY created_at DESC").all() as User[];
}

export function getUserStats(): {
  total: number;
  premium: number;
  active_today: number;
  banned: number;
} {
  const db = getDatabase();
  const today = new Date().toISOString().split("T")[0];
  const total = (db.prepare("SELECT COUNT(*) as count FROM users").get() as { count: number }).count;
  const premium = (
    db.prepare("SELECT COUNT(*) as count FROM users WHERE is_premium = 1").get() as { count: number }
  ).count;
  const active_today = (
    db.prepare("SELECT COUNT(*) as count FROM users WHERE last_request_date = ?").get(today) as {
      count: number;
    }
  ).count;
  const banned = (
    db.prepare("SELECT COUNT(*) as count FROM users WHERE is_banned = 1").get() as { count: number }
  ).count;
  return { total, premium, active_today, banned };
}

export function canUserMakeRequest(telegramId: number, maxFreeRequests: number): boolean {
  const user = getUser(telegramId);
  if (!user) return true;
  if (user.is_banned) return false;
  if (user.is_premium) return true;
  return user.daily_requests < maxFreeRequests;
}
