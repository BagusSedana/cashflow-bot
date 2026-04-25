import { getDatabase } from "./index";

export interface UsageLog {
  id: number;
  user_id: number;
  feature: string;
  tokens_used: number;
  cost_estimate: number;
  created_at: string;
}

export function logUsage(
  userId: number,
  feature: string,
  tokensUsed: number = 0,
  costEstimate: number = 0
): void {
  const db = getDatabase();
  db.prepare(
    "INSERT INTO usage_logs (user_id, feature, tokens_used, cost_estimate) VALUES (?, ?, ?, ?)"
  ).run(userId, feature, tokensUsed, costEstimate);
}

export function getUsageStats(): {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  by_feature: { feature: string; count: number; tokens: number; cost: number }[];
} {
  const db = getDatabase();

  const totals = db
    .prepare(
      "SELECT COUNT(*) as total_requests, COALESCE(SUM(tokens_used), 0) as total_tokens, COALESCE(SUM(cost_estimate), 0) as total_cost FROM usage_logs"
    )
    .get() as { total_requests: number; total_tokens: number; total_cost: number };

  const by_feature = db
    .prepare(
      "SELECT feature, COUNT(*) as count, COALESCE(SUM(tokens_used), 0) as tokens, COALESCE(SUM(cost_estimate), 0) as cost FROM usage_logs GROUP BY feature ORDER BY count DESC"
    )
    .all() as { feature: string; count: number; tokens: number; cost: number }[];

  return { ...totals, by_feature };
}

export function getUsageByDate(days: number = 30): { date: string; count: number; tokens: number }[] {
  const db = getDatabase();
  return db
    .prepare(
      `SELECT DATE(created_at) as date, COUNT(*) as count, COALESCE(SUM(tokens_used), 0) as tokens
       FROM usage_logs
       WHERE created_at >= datetime('now', '-' || ? || ' days')
       GROUP BY DATE(created_at)
       ORDER BY date ASC`
    )
    .all(days) as { date: string; count: number; tokens: number }[];
}

export function getUserUsage(
  userId: number
): { feature: string; count: number; tokens: number; cost: number }[] {
  const db = getDatabase();
  return db
    .prepare(
      "SELECT feature, COUNT(*) as count, COALESCE(SUM(tokens_used), 0) as tokens, COALESCE(SUM(cost_estimate), 0) as cost FROM usage_logs WHERE user_id = ? GROUP BY feature"
    )
    .all(userId) as { feature: string; count: number; tokens: number; cost: number }[];
}
