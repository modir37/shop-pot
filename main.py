import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

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

def start(update: Update, context):
    keyboard = [[InlineKeyboardButton("خرید کتاب - ۱۰۰,۰۰۰ تومان", callback_data="buy")]]
    update.message.reply_text(
        "فروشگاه آموزشی (تست)\nبرای خرید کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button_handler(update: Update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == "buy":
        query.edit_message_text("در حال انتقال به درگاه (تست)...")
        query.message.reply_text("پرداخت موفق! (تست)\nفایل در حال ارسال...")
        
        try:
            with open(PDF_FILE, 'rb') as pdf:
                query.message.reply_document(pdf, caption="کتاب شما با موفقیت ارسال شد!")
        except Exception as e:
            query.message.reply_text(f"خطا در ارسال فایل: {e}")
        
        context.bot.send_message(ADMIN_ID, f"خرید جدید از: {query.from_user.first_name}")

def main():
    # اجرای وب سرور در پس‌زمینه
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # اجرای ربات تلگرام با نسخه پایدار
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ ربات ۲۴ ساعته روشن شد!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

