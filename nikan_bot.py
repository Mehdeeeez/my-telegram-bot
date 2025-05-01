from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# سوالات به همراه گزینه‌ها
QUESTIONS = [
    ("👤 نام و نام خانوادگی کارفرما را وارد کن لطفاً:", []),
    ("🎭 دوست داری فضای فروشگاهت چه حسی داشته باشه؟", ["💎 لوکس و مجلل", "🔥 گرم و صمیمی", "📐 حرفه‌ای و مینیمال", "🎨 خلاق و متفاوت", "🏛 کلاسیک و باوقار"]),
    ("🎨 چه رنگ‌هایی رو بیشتر می‌پسندی برای فضای غالب؟", ["⚪️ سفید / کرم", "⚫️ خاکستری / مشکی", "✨ طلایی / برنزی", "🔵 آبی / سرمه‌ای", "🌳 رنگ‌های طبیعی چوبی"]),
    ("🧱 با چه متریال‌هایی حس خوبی داری؟", ["🪨 سنگ مرمر", "🔩 فلز براق", "🪵 چوب طبیعی", "🪞 شیشه و آینه", "🧱 بتن اکسپوز"]),
    ("💡 برای نورپردازی فروشگاه چه مدلی رو ترجیح می‌دی؟", ["🌟 نور مخفی", "🎯 نور متمرکز روی ویترین‌ها", "💎 لوستر خاص", "☀️ نور طبیعی", "🔄 ترکیبی"]),
    ("🪞 فرم ویترین‌ها چطوری باشه؟", ["📏 ویترین خطی", "🧲 استند مرکزی", "🧱 ویترین دیواری", "🪜 شلف شناور"]),
    ("🪑 مبلمان فروشگاه چه سبکی باشه؟", ["🛋 کلاسیک چرمی", "🪟 مدرن صاف", "🪶 مخملی و لوکس", "🔲 مینیمال ساده", "🚫 بدون مبلمان"]),
    ("🏷 لوگو و برندینگ فروشگاه چطور توی طراحی دیده بشه؟", ["🎯 برجسته و مرکزی", "🖼 پس‌زمینه هنری", "🧾 مینیمال", "🏛 جزء معماری"]),
    ("🔧 دوست داری از چه تکنولوژی‌هایی در طراحی استفاده بشه؟", ["🖥 مانیتور لمسی", "💡 نورپردازی هوشمند", "📷 دوربین هوشمند", "🤝 تعامل با مشتری", "🎛 کنترل از راه دور", "🎧 صدا و موسیقی هوشمند", "📶 اینترنت اشیاء (IoT)", "🕹 سنسور حضور مشتری"]),
    ("🌀 چه نوع بافت یا الگوهایی برات جذابه؟", ["🧊 صاف و یکدست", "🪵 بافت‌دار", "📐 الگوهای هندسی", "🌊 منحنی و نرم"]),
    ("💰 محدوده بودجه‌ات برای طراحی چقدره؟", ["💸 اقتصادی", "💳 متوسط", "💎 لوکس"]),
]

user_data = {}

ALL_STYLES = ["مدرن", "کلاسیک", "لوکس", "مینیمال", "خلاق"]

def infer_style(answers):
    score = {style: 0 for style in ALL_STYLES}
    keywords = {
        "مدرن": ["مدرن", "صاف", "نور مخفی", "فلز", "تکنولوژی", "هندسی"],
        "کلاسیک": ["کلاسیک", "لوستر", "چرم", "برجسته"],
        "لوکس": ["طلایی", "مخملی", "لوکس", "سنگ مرمر"],
        "مینیمال": ["ساده", "مینیمال", "خاکستری", "کمینه"],
        "خلاق": ["متفاوت", "تعامل", "منحنی"]
    }
    for ans in answers:
        for style, kws in keywords.items():
            if any(kw in ans for kw in kws):
                score[style] += 1
    best_style = max(score, key=score.get)
    return best_style

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"answers": [], "step": 0}
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = user_data[user_id]["step"]
    if step >= len(QUESTIONS):
        return await show_result(update, context)
    question, options = QUESTIONS[step]
    if step == 0:
        await update.message.reply_text(question)
    else:
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
        keyboard.append([InlineKeyboardButton("🔁 شروع مجدد", callback_data="restart")])
        markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text(question, reply_markup=markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(question, reply_markup=markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    answer = query.data
    if answer == "restart":
        return await restart_button(update, context)
    user_data[user_id]["answers"].append(answer)
    user_data[user_id]["step"] += 1
    return await ask_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answers = user_data[user_id]["answers"]
    name = answers[0]
    summary = "\n".join([
        f"{i}. {QUESTIONS[i][0]} \n➤ {answers[i]}"
        for i in range(1, len(answers))
    ])
    inferred_style = infer_style(answers)
    final_msg = (
        f"✨ نام شما: {name}\n\n"
        f"🎯 سبک پیشنهادی طراحی فروشگاه‌تون: [{inferred_style}]\n"
        f"(از بین تمامی سبک‌های طراحی: {', '.join(ALL_STYLES)})\n\n"
        f"{summary}\n\n"
        "✅ لطفاً این نتیجه رو برای ادامه طراحی به شماره 09912076069 ارسال کن تا طراحی اختصاصی‌ت شروع شه 🙌"
    )
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 شروع مجدد", callback_data="restart")]])
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(final_msg, reply_markup=markup)
    elif hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(final_msg, reply_markup=markup)
    return ConversationHandler.END

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_data.get(user_id, {}).get("step") == 0:
        user_data[user_id]["answers"].append(update.message.text)
        user_data[user_id]["step"] += 1
        return await ask_question(update, context)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"answers": [], "step": 0}
    await update.message.reply_text("خب از اول شروع می‌کنیم 😊")
    return await ask_question(update, context)

async def restart_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data[query.from_user.id] = {"answers": [], "step": 0}
    await query.edit_message_text("خب از اول شروع می‌کنیم 😊")
    return await ask_question(update, context)

def main():
    app = ApplicationBuilder().token("8117814099:AAFDNpSqSkBgW7echAB0kEzqndBm_nbD0h4").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(restart_button, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == '__main__':
    main()
