import OpenAI from "openai";
import { config } from "../config";
import { logger } from "../utils/logger";

let client: OpenAI;

export function getOpenAIClient(): OpenAI {
  if (!client) {
    client = new OpenAI({ apiKey: config.openai.apiKey });
  }
  return client;
}

export async function chatCompletion(
  messages: { role: "system" | "user" | "assistant"; content: string }[],
  systemPrompt?: string
): Promise<{ content: string; tokensUsed: number }> {
  const openai = getOpenAIClient();

  const allMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [];

  if (systemPrompt) {
    allMessages.push({ role: "system", content: systemPrompt });
  }

  allMessages.push(...messages);

  try {
    const response = await openai.chat.completions.create({
      model: config.openai.chatModel,
      messages: allMessages,
      max_tokens: 2048,
      temperature: 0.7,
    });

    const content = response.choices[0]?.message?.content || "No response generated.";
    const tokensUsed = response.usage?.total_tokens || 0;

    return { content, tokensUsed };
  } catch (error) {
    logger.error(`ChatGPT API error: ${error}`);
    throw new Error("Failed to generate AI response. Please try again later.");
  }
}

export async function summarizeText(text: string): Promise<{ content: string; tokensUsed: number }> {
  return chatCompletion(
    [{ role: "user", content: text }],
    "You are a helpful assistant that summarizes text concisely. Provide a clear, well-structured summary of the given text. Keep it brief but comprehensive."
  );
}

export async function translateText(
  text: string,
  targetLanguage: string
): Promise<{ content: string; tokensUsed: number }> {
  return chatCompletion(
    [{ role: "user", content: text }],
    `You are a professional translator. Translate the following text to ${targetLanguage}. Only output the translation, nothing else.`
  );
}

export async function generateImage(
  prompt: string
): Promise<{ url: string; revisedPrompt: string }> {
  const openai = getOpenAIClient();

  try {
    const response = await openai.images.generate({
      model: config.openai.imageModel,
      prompt,
      n: 1,
      size: "1024x1024",
      quality: "standard",
    });

    const url = response.data?.[0]?.url;
    const revisedPrompt = response.data?.[0]?.revised_prompt || prompt;

    if (!url) {
      throw new Error("No image URL in response");
    }

    return { url, revisedPrompt };
  } catch (error) {
    logger.error(`DALL-E API error: ${error}`);
    throw new Error("Failed to generate image. Please try again with a different prompt.");
  }
}

export async function textToSpeech(text: string): Promise<Buffer> {
  const openai = getOpenAIClient();

  try {
    const response = await openai.audio.speech.create({
      model: config.openai.ttsModel,
      voice: config.openai.ttsVoice,
      input: text,
      response_format: "mp3",
    });

    const arrayBuffer = await response.arrayBuffer();
    return Buffer.from(arrayBuffer);
  } catch (error) {
    logger.error(`TTS API error: ${error}`);
    throw new Error("Failed to generate speech. Please try again later.");
  }
}

export async function analyzeCode(code: string): Promise<{ content: string; tokensUsed: number }> {
  return chatCompletion(
    [{ role: "user", content: `\`\`\`\n${code}\n\`\`\`` }],
    "You are a senior software engineer. Analyze the given code and provide: 1) What it does, 2) Potential issues or bugs, 3) Suggestions for improvement. Be concise and practical."
  );
}
