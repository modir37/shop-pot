import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PDF_FILE = "book.pdf"

# ایجاد وب سرور برای Render
web_app = Flask(name)

@web_app.route('/')
def home():
    return "✅ ربات فروشگاه روشن است!"

def run_web():
    web_app.run(host='0.0.0.0', port=5000, debug=False)

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
    
    try:
        with open(PDF_FILE, 'rb') as pdf:
            await query.message.reply_document(pdf, caption="کتاب شما با موفقیت ارسال شد!")
    except Exception as e:
        await query.message.reply_text(f"خطا: {e}")
    
    await context.bot.send_message(ADMIN_ID, f"خرید جدید: {query.from_user.first_name}")

def main():
    # اجرای وب سرور در پس‌زمینه
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # اجرای ربات تلگرام
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    
    print("✅ ربات ۲۴ ساعته روشن شد!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
