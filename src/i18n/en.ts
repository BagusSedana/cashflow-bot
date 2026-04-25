const en = {
  // Welcome & Help
  welcome: `🤖 *Welcome to AI Bot!*

I'm your AI-powered assistant with these features:

🧠 *Chat* — Ask me anything (powered by ChatGPT)
🎨 *Image* — Generate images from text
🔊 *Voice* — Convert text to speech
📝 *Summarize* — Summarize long texts
🌐 *Translate* — Translate between languages
💻 *Code* — Analyze and explain code

Use /help to see all commands.`,

  help: `📋 *Available Commands:*

*AI Features:*
/ask <question> — Ask AI anything
/image <description> — Generate an image
/voice <text> — Convert text to speech
/summarize <text> — Summarize text
/translate <lang> <text> — Translate text
/code <code> — Analyze code

*Account:*
/usage — View your usage stats
/premium — Upgrade to premium
/language — Change language
/clear — Clear conversation history

*General:*
/start — Welcome message
/help — Show this help`,

  // Features
  ask_prompt: "💬 What would you like to ask? Send me your question.",
  ask_thinking: "🤔 Thinking...",
  image_prompt: "🎨 Describe the image you want to generate:",
  image_generating: "🎨 Generating your image...",
  image_revised: "📝 *Revised prompt:* ",
  voice_prompt: "🔊 Send me the text you want to convert to speech:",
  voice_generating: "🔊 Generating speech...",
  summarize_prompt: "📝 Send me the text you want to summarize:",
  summarize_processing: "📝 Summarizing...",
  translate_prompt: "🌐 Usage: /translate <language> <text>\nExample: /translate Spanish Hello, how are you?",
  translate_processing: "🌐 Translating...",
  code_prompt: "💻 Send me the code you want to analyze:",
  code_analyzing: "💻 Analyzing code...",

  // Limits & Premium
  limit_reached: `⚠️ *Daily limit reached!*

You've used all your free requests for today.

🌟 *Upgrade to Premium* for unlimited access!
Use /premium for details.`,

  premium_info: `🌟 *Premium Plan*

✅ Unlimited AI requests
✅ Priority response time
✅ HD image generation
✅ Longer conversation memory
✅ Priority support

💰 *Price:* $PRICE/month

Contact the admin to upgrade!`,

  already_premium: "✅ You already have premium access! Expires: ",

  // Usage
  usage_title: "📊 *Your Usage Stats:*",
  usage_requests_today: "Today's requests: ",
  usage_total: "Total requests: ",
  usage_account_type: "Account type: ",
  usage_premium: "⭐ Premium",
  usage_free: "Free",

  // Settings
  language_changed: "✅ Language changed to English!",
  language_select: "🌐 Select your language:",
  conversation_cleared: "🗑️ Conversation history cleared!",

  // Errors
  error_generic: "❌ Something went wrong. Please try again later.",
  error_banned: "🚫 Your account has been suspended. Contact admin for support.",
  error_empty_message: "Please provide a message after the command.",

  // Admin
  admin_only: "⛔ This command is for admins only.",
};

export default en;
