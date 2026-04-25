import { Context, NextFunction } from "grammy";
import { findOrCreateUser, canUserMakeRequest, incrementUserRequests } from "../database/users";
import { config } from "../config";
import { t } from "../i18n";
import { logger } from "../utils/logger";

export interface BotContext extends Context {
  user: {
    telegramId: number;
    language: string;
    isPremium: boolean;
  };
}

const rateLimitMap = new Map<number, { count: number; resetAt: number }>();

export async function userMiddleware(ctx: BotContext, next: NextFunction): Promise<void> {
  if (!ctx.from) return;

  const user = findOrCreateUser(
    ctx.from.id,
    ctx.from.username,
    ctx.from.first_name,
    ctx.from.last_name
  );

  if (user.is_banned) {
    await ctx.reply(t("error_banned", user.language));
    return;
  }

  ctx.user = {
    telegramId: ctx.from.id,
    language: user.language,
    isPremium: user.is_premium === 1,
  };

  await next();
}

export async function rateLimitMiddleware(ctx: BotContext, next: NextFunction): Promise<void> {
  if (!ctx.from) return;

  const userId = ctx.from.id;
  const now = Date.now();
  const entry = rateLimitMap.get(userId);

  if (entry && now < entry.resetAt) {
    if (entry.count >= config.rateLimit.maxRequests) {
      await ctx.reply("⏳ Too many requests. Please wait a moment.");
      return;
    }
    entry.count++;
  } else {
    rateLimitMap.set(userId, { count: 1, resetAt: now + config.rateLimit.windowMs });
  }

  await next();
}

export async function usageLimitMiddleware(ctx: BotContext, next: NextFunction): Promise<void> {
  if (!ctx.from) return;

  if (!canUserMakeRequest(ctx.from.id, config.bot.maxFreeRequests)) {
    const lang = ctx.user?.language || "en";
    await ctx.reply(t("limit_reached", lang), { parse_mode: "Markdown" });
    return;
  }

  incrementUserRequests(ctx.from.id);
  await next();
}

export async function errorMiddleware(err: Error, ctx: BotContext): Promise<void> {
  logger.error(`Bot error for user ${ctx.from?.id}: ${err.message}`, { stack: err.stack });
  const lang = ctx.user?.language || "en";
  try {
    await ctx.reply(t("error_generic", lang));
  } catch {
    logger.error("Failed to send error message to user");
  }
}
