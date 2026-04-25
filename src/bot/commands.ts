import { Bot, InputFile } from "grammy";
import { BotContext } from "./middleware";
import { t } from "../i18n";
import { config } from "../config";
import {
  chatCompletion,
  generateImage,
  textToSpeech,
  summarizeText,
  translateText,
  analyzeCode,
} from "../ai/openai";
import {
  addMessage,
  getConversationHistory,
  clearConversation,
} from "../database/conversations";
import { logUsage } from "../database/usage";
import { getUser, updateUserLanguage } from "../database/users";
import { getSupportedLanguages } from "../i18n";
import { logger } from "../utils/logger";

export function registerCommands(bot: Bot<BotContext>): void {
  bot.command("start", handleStart);
  bot.command("help", handleHelp);
  bot.command("ask", handleAsk);
  bot.command("image", handleImage);
  bot.command("voice", handleVoice);
  bot.command("summarize", handleSummarize);
  bot.command("translate", handleTranslate);
  bot.command("code", handleCode);
  bot.command("usage", handleUsage);
  bot.command("premium", handlePremium);
  bot.command("language", handleLanguage);
  bot.command("clear", handleClear);

  // Handle plain text messages as chat
  bot.on("message:text", handleTextMessage);
}

async function handleStart(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  await ctx.reply(t("welcome", lang), { parse_mode: "Markdown" });
}

async function handleHelp(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  await ctx.reply(t("help", lang), { parse_mode: "Markdown" });
}

async function handleAsk(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const question = ctx.match as string;

  if (!question?.trim()) {
    await ctx.reply(t("ask_prompt", lang));
    return;
  }

  await processChat(ctx, question);
}

async function handleTextMessage(ctx: BotContext): Promise<void> {
  const text = ctx.message?.text;
  if (!text || text.startsWith("/")) return;
  await processChat(ctx, text);
}

async function processChat(ctx: BotContext, userMessage: string): Promise<void> {
  const lang = ctx.user.language;
  const userId = ctx.user.telegramId;

  const thinkingMsg = await ctx.reply(t("ask_thinking", lang));

  try {
    const history = getConversationHistory(userId, 10);
    const messages = history
      .reverse()
      .map((msg) => ({
        role: msg.role as "user" | "assistant",
        content: msg.content,
      }));
    messages.push({ role: "user", content: userMessage });

    const systemPrompt =
      "You are a helpful, friendly AI assistant. Be concise but thorough. If the user writes in a specific language, respond in that same language.";

    const { content, tokensUsed } = await chatCompletion(messages, systemPrompt);

    addMessage(userId, "user", userMessage);
    addMessage(userId, "assistant", content, tokensUsed);
    logUsage(userId, "chat", tokensUsed, tokensUsed * 0.000001);

    await ctx.api.editMessageText(ctx.chat!.id, thinkingMsg.message_id, content, {
      parse_mode: "Markdown",
    }).catch(async () => {
      // Fallback if Markdown parsing fails
      await ctx.api.editMessageText(ctx.chat!.id, thinkingMsg.message_id, content);
    });
  } catch (error) {
    logger.error(`Chat error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, thinkingMsg.message_id, t("error_generic", lang));
  }
}

async function handleImage(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const prompt = ctx.match as string;

  if (!prompt?.trim()) {
    await ctx.reply(t("image_prompt", lang));
    return;
  }

  const statusMsg = await ctx.reply(t("image_generating", lang));

  try {
    const { url, revisedPrompt } = await generateImage(prompt);

    logUsage(ctx.user.telegramId, "image", 0, 0.04);

    await ctx.replyWithPhoto(url, {
      caption: `${t("image_revised", lang)}${revisedPrompt}`,
      parse_mode: "Markdown",
    });

    await ctx.api.deleteMessage(ctx.chat!.id, statusMsg.message_id).catch(() => {});
  } catch (error) {
    logger.error(`Image generation error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, t("error_generic", lang));
  }
}

async function handleVoice(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const text = ctx.match as string;

  if (!text?.trim()) {
    await ctx.reply(t("voice_prompt", lang));
    return;
  }

  const statusMsg = await ctx.reply(t("voice_generating", lang));

  try {
    const audioBuffer = await textToSpeech(text);

    logUsage(ctx.user.telegramId, "tts", text.length, text.length * 0.000015);

    await ctx.replyWithAudio(new InputFile(audioBuffer, "speech.mp3"), {
      title: "AI Generated Speech",
    });

    await ctx.api.deleteMessage(ctx.chat!.id, statusMsg.message_id).catch(() => {});
  } catch (error) {
    logger.error(`TTS error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, t("error_generic", lang));
  }
}

async function handleSummarize(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const text = ctx.match as string;

  if (!text?.trim()) {
    await ctx.reply(t("summarize_prompt", lang));
    return;
  }

  const statusMsg = await ctx.reply(t("summarize_processing", lang));

  try {
    const { content, tokensUsed } = await summarizeText(text);

    logUsage(ctx.user.telegramId, "summarize", tokensUsed, tokensUsed * 0.000001);

    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, `📝 *Summary:*\n\n${content}`, {
      parse_mode: "Markdown",
    }).catch(async () => {
      await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, `📝 Summary:\n\n${content}`);
    });
  } catch (error) {
    logger.error(`Summarize error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, t("error_generic", lang));
  }
}

async function handleTranslate(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const input = ctx.match as string;

  if (!input?.trim()) {
    await ctx.reply(t("translate_prompt", lang));
    return;
  }

  const parts = input.split(" ");
  const targetLang = parts[0];
  const text = parts.slice(1).join(" ");

  if (!text.trim()) {
    await ctx.reply(t("translate_prompt", lang));
    return;
  }

  const statusMsg = await ctx.reply(t("translate_processing", lang));

  try {
    const { content, tokensUsed } = await translateText(text, targetLang);

    logUsage(ctx.user.telegramId, "translate", tokensUsed, tokensUsed * 0.000001);

    await ctx.api.editMessageText(
      ctx.chat!.id,
      statusMsg.message_id,
      `🌐 *Translation (${targetLang}):*\n\n${content}`,
      { parse_mode: "Markdown" }
    ).catch(async () => {
      await ctx.api.editMessageText(
        ctx.chat!.id,
        statusMsg.message_id,
        `🌐 Translation (${targetLang}):\n\n${content}`
      );
    });
  } catch (error) {
    logger.error(`Translate error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, t("error_generic", lang));
  }
}

async function handleCode(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const code = ctx.match as string;

  if (!code?.trim()) {
    await ctx.reply(t("code_prompt", lang));
    return;
  }

  const statusMsg = await ctx.reply(t("code_analyzing", lang));

  try {
    const { content, tokensUsed } = await analyzeCode(code);

    logUsage(ctx.user.telegramId, "code", tokensUsed, tokensUsed * 0.000001);

    await ctx.api.editMessageText(
      ctx.chat!.id,
      statusMsg.message_id,
      `💻 *Code Analysis:*\n\n${content}`,
      { parse_mode: "Markdown" }
    ).catch(async () => {
      await ctx.api.editMessageText(
        ctx.chat!.id,
        statusMsg.message_id,
        `💻 Code Analysis:\n\n${content}`
      );
    });
  } catch (error) {
    logger.error(`Code analysis error: ${error}`);
    await ctx.api.editMessageText(ctx.chat!.id, statusMsg.message_id, t("error_generic", lang));
  }
}

async function handleUsage(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const user = getUser(ctx.user.telegramId);

  if (!user) return;

  const accountType = user.is_premium ? t("usage_premium", lang) : t("usage_free", lang);

  const message = `${t("usage_title", lang)}

${t("usage_requests_today", lang)}${user.daily_requests}/${user.is_premium ? "∞" : config.bot.maxFreeRequests}
${t("usage_total", lang)}${user.total_requests}
${t("usage_account_type", lang)}${accountType}`;

  await ctx.reply(message, { parse_mode: "Markdown" });
}

async function handlePremium(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  const user = getUser(ctx.user.telegramId);

  if (user?.is_premium) {
    await ctx.reply(`${t("already_premium", lang)}${user.premium_expires_at || "∞"}`, {
      parse_mode: "Markdown",
    });
    return;
  }

  const info = t("premium_info", lang).replace("$PRICE", config.bot.premiumPrice.toString());
  await ctx.reply(info, { parse_mode: "Markdown" });
}

async function handleLanguage(ctx: BotContext): Promise<void> {
  const languages = getSupportedLanguages();

  const keyboard = languages.map((lang) => [
    { text: `${lang.name}`, callback_data: `lang_${lang.code}` },
  ]);

  await ctx.reply(t("language_select", ctx.user.language), {
    reply_markup: { inline_keyboard: keyboard },
  });
}

async function handleClear(ctx: BotContext): Promise<void> {
  const lang = ctx.user.language;
  clearConversation(ctx.user.telegramId);
  await ctx.reply(t("conversation_cleared", lang));
}

export function registerCallbacks(bot: Bot<BotContext>): void {
  bot.callbackQuery(/^lang_(.+)$/, async (ctx) => {
    const langCode = ctx.match[1];
    updateUserLanguage(ctx.user.telegramId, langCode);
    ctx.user.language = langCode;
    await ctx.answerCallbackQuery({ text: "✅" });
    await ctx.editMessageText(t("language_changed", langCode));
  });
}
