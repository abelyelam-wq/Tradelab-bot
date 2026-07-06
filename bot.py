import os
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "⚡ *TradeLab AI Bot Commands* ⚡\n\n"
        "/start \- Welcome screen and current trader rank\n"
        "/help \- Display this breakdown list\n"
        "/quiz \- Challenge yourself with an SMC technical question\n"
        "/coach `<prompt>` \- Consult your senior Wall Street AI Coach\n"
        "/journal_add `<text>` \- Log a trade setup into your trading journal\n"
        "/journal \- Review your stored journal entries\n\n"
        "📷 *Tip:* Send a chart screenshot directly to run the AI Vision Market Structure Filter (BOS, CHoCH, FVG, OB detection)!"
    )
    await update.message.reply_text(help_text, parse_mode="MarkdownV2")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *SMC QUIZ QUESTION:*\n\n"
        "When price breaks a major structural swing high or swing low to *continue* the existing trend, what is this called?"
    )
    keyboard = [
        [InlineKeyboardButton("A) CHoCH (Change of Character)", callback_data="quiz_wrong")],
        [InlineKeyboardButton("B) BOS (Break of Structure)", callback_data="quiz_correct")],
        [InlineKeyboardButton("C) FVG (Fair Value Gap)", callback_data="quiz_wrong")],
        [InlineKeyboardButton("D) Liquidity Sweep", callback_data="quiz_wrong")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def coach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("❌ Please provide a question or trade scenario. Example: `/coach Should I enter at an H4 FVG?`", parse_mode="Markdown")
        return
        
    if not GEMINI_API_KEY:
        await update.message.reply_text("⚠️ Gemini AI Mentor is currently offline (API key missing). Contact admin.")
        return

    await update.message.reply_chat_action("typing")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"You are a Senior Wall Street Institutional FX Trader and elite Smart Money Concepts (SMC) coach. "
            f"Provide professional, analytical, and highly precise mentorship feedback regarding this inquiry: {user_text}"
        )
        response = model.generate_content(prompt)
        await update.message.reply_text(f"🧠 *AI Coach Response:*\n\n{response.text}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Gemini Coach Error: {e}")
        await update.message.reply_text("❌ Failed to process request with AI Mentor.")

async def journal_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entry_text = " ".join(context.args)
    if not entry_text:
        await update.message.reply_text("❌ Please specify your journal notes. Example: `/journal_add XAUUSD bought at 2320 OB, targeting 2350.`", parse_mode="Markdown")
        return
        
    user = update.effective_user
    profile = get_user_profile(user.id, user.username or user.first_name)
    profile["journal"].append(entry_text)
    profile["xp"] += 50
    update_user_profile(user.id, profile)
    
    await update.message.reply_text(f"✅ *Logged to Journal!* (+50 XP gained). Total: `{profile['xp']} XP`.", parse_mode="Markdown")

async def journal_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    profile = get_user_profile(user.id, user.username or user.first_name)
    
    if not profile["journal"]:
        await update.message.reply_text("📓 Your SMC trading journal is empty. Use /journal_add to log setups!")
        return
        
    entries = "\n\n".join([f"📌 *Entry {i+1}:* {text}" for i, text in enumerate(profile["journal"])])
    await update.message.reply_text(f"📓 *Your Trading Journal Logs:*\n\n{entries}", parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GEMINI_API_KEY:
        await update.message.reply_text("⚠️ AI Vision Market Structure Filter is offline (Missing Gemini API key).")
        return

    await update.message.reply_text("📸 *Analyzing chart screenshot via Gemini 1.5 Flash Vision... Checking for BOS, CHoCH, Order Blocks, and FVGs...*", parse_mode="Markdown")
    await update.message.reply_chat_action("typing")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Analyze this financial asset trading chart screenshot using Smart Money Concepts (SMC). "
            "Identify major Market Structures like Break of Structure (BOS), Change of Character (CHoCH), "
            "valid Order Blocks (OB), and Fair Value Gaps (FVG). Provide a structured technical summary and actionable insight."
        )
        
        response = model.generate_content([prompt, image])
        await update.message.reply_text(f"🔍 *AI Vision Market Structure Analysis:*\n\n{response.text}", parse_mode="Markdown")
        
        user = update.effective_user
        profile = get_user_profile(user.id, user.username or user.first_name)
        profile["xp"] += 100
        update_user_profile(user.id, profile)
        
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        await update.message.reply_text("❌ Error analyzing chart screenshot. Make sure it's a clear image.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    profile = get_user_profile(user.id, user.username or user.first_name)
    
    if query.data == "start_quiz":
        await quiz(update, context)
    elif query.data == "view_profile":
        text = (
            f"📊 *Trader Profile: @{profile['username']}*\n\n"
            f"🏆 Rank: `{profile['current_level']}`\n"
            f"✨ Experience: `{profile['xp']} XP`\n"
            f"🔥 Learning Streak: `{profile['streak']} days`\n\n"
            f"🧠 Patience: `{profile['patience_score']}/100`\n"
            f"⚡ Confidence: `{profile['confidence_score']}/100`\n"
            f"🛡️ Risk Control: `{profile['risk_score']}/100`\n"
            f"🧘 Psychology: `{profile['psychology_score']}/100`"
        )
        await query.message.reply_text(text, parse_mode="Markdown")
    elif query.data == "ai_mentor":
        await query.message.reply_text("🧠 To consult your AI mentor, use the command: `/coach Your question here`\nExample: `/coach What is a premium vs discount zone?`", parse_mode="Markdown")
    elif query.data == "view_journal":
        if not profile["journal"]:
            await query.message.reply_text("📓 Your journal is empty. Use `/journal_add <notes>` to start.")
        else:
            entries = "\n\n".join([f"📌 *Entry {i+1}:* {text}" for i, text in enumerate(profile["journal"])])
            await query.message.reply_text(f"📓 *Your Trading Journal Logs:*\n\n{entries}", parse_mode="Markdown")
    elif query.data == "quiz_correct":
        profile["xp"] += 150
        update_user_profile(user.id, profile)
        await query.message.edit_text(f"🎉 *Correct!* Break of Structure (BOS) indicates trend continuation. You gained +150 XP! Total: `{profile['xp']} XP`.", parse_mode="Markdown")
    elif query.data == "quiz_wrong":
        await query.message.edit_text("❌ *Incorrect.* Try again! (Hint: CHoCH is a trend reversal, while continuation is a Break of Structure). Use /quiz to retry.", parse_mode="Markdown")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN is missing!")
        return

    print("Starting TradeLab AI Bot on production Telegram...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("coach", coach))
    app.add_handler(CommandHandler("journal_add", journal_add))
    app.add_handler(CommandHandler("journal", journal_view))
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is live and polling messages...")
    app.run_polling()

if __name__ == '__main__':
    main()
