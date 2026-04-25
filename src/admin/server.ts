import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import path from "path";
import { config } from "../config";
import { logger } from "../utils/logger";
import { getAllUsers, getUserStats, banUser, unbanUser, setUserPremium, removeUserPremium } from "../database/users";
import { getUsageStats, getUsageByDate } from "../database/usage";
import { getConversationCount } from "../database/conversations";

export function createAdminServer(): express.Application {
  const app = express();

  app.use(cors());
  app.use(express.json());
  app.use(express.static(path.join(__dirname, "../../admin")));

  // Basic auth middleware
  const auth = (req: Request, res: Response, next: NextFunction): void => {
    const authHeader = req.headers.authorization;
    if (!authHeader) {
      res.status(401).json({ error: "Authorization required" });
      return;
    }

    const encoded = authHeader.split(" ")[1];
    if (!encoded) {
      res.status(401).json({ error: "Invalid authorization" });
      return;
    }

    const decoded = Buffer.from(encoded, "base64").toString();
    const [username, password] = decoded.split(":");

    if (username !== config.admin.username || password !== config.admin.password) {
      res.status(401).json({ error: "Invalid credentials" });
      return;
    }

    next();
  };

  // API Routes
  app.get("/api/stats", auth, (_req: Request, res: Response) => {
    const userStats = getUserStats();
    const usageStats = getUsageStats();
    const conversationCount = getConversationCount();

    res.json({
      users: userStats,
      usage: usageStats,
      conversations: conversationCount,
    });
  });

  app.get("/api/users", auth, (_req: Request, res: Response) => {
    const users = getAllUsers();
    res.json(users);
  });

  app.post("/api/users/:telegramId/ban", auth, (req: Request, res: Response) => {
    const telegramId = parseInt(req.params.telegramId as string, 10);
    banUser(telegramId);
    res.json({ success: true });
  });

  app.post("/api/users/:telegramId/unban", auth, (req: Request, res: Response) => {
    const telegramId = parseInt(req.params.telegramId as string, 10);
    unbanUser(telegramId);
    res.json({ success: true });
  });

  app.post("/api/users/:telegramId/premium", auth, (req: Request, res: Response) => {
    const telegramId = parseInt(req.params.telegramId as string, 10);
    const { expiresAt } = req.body;
    setUserPremium(telegramId, expiresAt);
    res.json({ success: true });
  });

  app.post("/api/users/:telegramId/remove-premium", auth, (req: Request, res: Response) => {
    const telegramId = parseInt(req.params.telegramId as string, 10);
    removeUserPremium(telegramId);
    res.json({ success: true });
  });

  app.get("/api/usage/chart", auth, (req: Request, res: Response) => {
    const days = parseInt((req.query.days as string) || "30", 10);
    const data = getUsageByDate(days);
    res.json(data);
  });

  // Serve admin dashboard
  app.get("*", (_req: Request, res: Response) => {
    res.sendFile(path.join(__dirname, "../../admin/index.html"));
  });

  return app;
}

export function startAdminServer(app: express.Application): void {
  app.listen(config.admin.port, () => {
    logger.info(`Admin dashboard running at http://localhost:${config.admin.port}`);
  });
}
