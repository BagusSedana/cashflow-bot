import { getDatabase } from "./index";

export interface Conversation {
  id: number;
  user_id: number;
  role: string;
  content: string;
  tokens_used: number;
  created_at: string;
}

export function addMessage(
  userId: number,
  role: "user" | "assistant" | "system",
  content: string,
  tokensUsed: number = 0
): void {
  const db = getDatabase();
  db.prepare("INSERT INTO conversations (user_id, role, content, tokens_used) VALUES (?, ?, ?, ?)").run(
    userId,
    role,
    content,
    tokensUsed
  );
}

export function getConversationHistory(userId: number, limit: number = 10): Conversation[] {
  const db = getDatabase();
  return db
    .prepare(
      "SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
    )
    .all(userId, limit) as Conversation[];
}

export function clearConversation(userId: number): void {
  const db = getDatabase();
  db.prepare("DELETE FROM conversations WHERE user_id = ?").run(userId);
}

export function getConversationCount(): number {
  const db = getDatabase();
  return (db.prepare("SELECT COUNT(*) as count FROM conversations").get() as { count: number }).count;
}
