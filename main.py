import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PDF_FILE = "book.pdf"

# ایجاد وب سرور برای Render
web_app = Flask(__name__)

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy":
        await query.edit_message_text("در حال انتقال به درگاه (تست)...")
        await query.message.reply_text("پرداخت موفق! (تست)\nفایل در حال ارسال...")
        
        try:
            with open(PDF_FILE, 'rb') as pdf:
                await query.message.reply_document(pdf, caption="کتاب شما با موفقیت ارسال شد!")
        except Exception as e:
            await query.message.reply_text(f"خطا در ارسال فایل: {e}")
        
        await context.bot.send_message(ADMIN_ID, f"خرید جدید از: {query.from_user.first_name}")

def main():
    # اجرای وب سرور در پس‌زمینه
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # اجرای ربات تلگرام
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ ربات ۲۴ ساعته روشن شد!")
    application.run_polling()

if __name__ == "__main__":
    main()


