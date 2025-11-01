import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# رازها از Replit Secrets میاد — با os.getenv
TOKEN = os.getenv("TOKEN")
MERCHANT_ID = os.getenv("MERCHANT_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

PDF_FILE = "book.pdf"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("خرید کتاب - ۱۰۰,۰۰۰ تومان", callback_data="buy")]]
    await update.message.reply_text(
        "فروشگاه آموزشی (تست)\nبرای خرید کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("در حال انتقال به درگاه (تست)...")
    await query.message.reply_text("پرداخت موفق! (تست)\nفایل در حال ارسال...")
    
    with open(PDF_FILE, 'rb') as pdf:
        await query.message.reply_document(pdf, caption="کتاب شما ارسال شد!")

    await context.bot.send_message(ADMIN_ID, f"خرید جدید: {query.from_user.first_name}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buy))

print("ربات ۲۴ ساعته روشن شد!")
app.run_polling()