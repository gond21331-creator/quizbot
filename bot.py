from telegram import Update, Poll
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import json
import os

# =========================
# अपनी जानकारी यहाँ भरो
# =========================

TOKEN = "8818845736:AAFbweonkTGp0QtCDrZgaro3zuUu5ryaDOM"
OWNER_ID = 7768335149

CONFIG_FILE = "config.json"


# =========================
# Group ID save/load
# =========================

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


config = load_config()


# =========================
# Start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Quiz Bot Ready!\n\n"
        "/setgroup - इस Group को quiz group बनाएं\n"
        "/addquiz - नई quiz बनाएं\n"
        "/cancel - quiz बनाना बंद करें"
    )


# =========================
# Set Group
# =========================

async def setgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ आप Owner नहीं हैं।")
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "❌ यह command अपने Quiz Group के अंदर चलाओ।"
        )
        return

    config["group_id"] = update.effective_chat.id
    save_config(config)

    await update.message.reply_text(
        "✅ यह Group Quiz Group के रूप में save हो गया है!"
    )


# =========================
# Add Quiz Start
# =========================

async def addquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ केवल Owner quiz add कर सकता है।")
        return

    if "group_id" not in config:
        await update.message.reply_text(
            "❌ पहले अपने Group में /setgroup command चलाओ।"
        )
        return

    context.user_data.clear()
    context.user_data["step"] = "question"

    await update.message.reply_text(
        "📝 Quiz Question भेजो:"
    )


# =========================
# Cancel
# =========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Quiz बनाना cancel कर दिया गया।"
    )


# =========================
# Quiz Creation
# =========================

async def quiz_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    step = context.user_data.get("step")

    if not step:
        return

    text = update.message.text.strip()

    # Question
    if step == "question":

        context.user_data["question"] = text
        context.user_data["step"] = "option1"

        await update.message.reply_text(
            "🔹 Option A भेजो:"
        )

    # Option A
    elif step == "option1":

        context.user_data["option1"] = text
        context.user_data["step"] = "option2"

        await update.message.reply_text(
            "🔹 Option B भेजो:"
        )

    # Option B
    elif step == "option2":

        context.user_data["option2"] = text
        context.user_data["step"] = "option3"

        await update.message.reply_text(
            "🔹 Option C भेजो:"
        )

    # Option C
    elif step == "option3":

        context.user_data["option3"] = text
        context.user_data["step"] = "option4"

        await update.message.reply_text(
            "🔹 Option D भेजो:"
        )

    # Option D
    elif step == "option4":

        context.user_data["option4"] = text
        context.user_data["step"] = "correct"

        await update.message.reply_text(
            "✅ सही answer बताओ:\n\n"
            "A / B / C / D में से कोई एक लिखो।"
        )

    # Correct Answer
    elif step == "correct":

        answer = text.upper()

        if answer not in ["A", "B", "C", "D"]:
            await update.message.reply_text(
                "❌ सिर्फ A, B, C या D लिखो।"
            )
            return

        correct_option = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3
        }[answer]

        question = context.user_data["question"]

        options = [
            context.user_data["option1"],
            context.user_data["option2"],
            context.user_data["option3"],
            context.user_data["option4"]
        ]

        group_id = config["group_id"]

        # Group में Telegram Quiz भेजना
        await context.bot.send_poll(
            chat_id=group_id,
            question=question,
            options=options,
            type=Poll.QUIZ,
            correct_option_id=correct_option,
            is_anonymous=False
        )

        await update.message.reply_text(
            "🎉 Quiz successfully Group में भेज दी गई!"
        )

        context.user_data.clear()


# =========================
# Main
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setgroup", setgroup))
    app.add_handler(CommandHandler("addquiz", addquiz))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            quiz_message
        )
    )

    print("🤖 Quiz Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
