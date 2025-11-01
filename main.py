import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PDF_FILE = "book.pdf"

# دیتابیس ساده در حافظه
user_data = {}

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ ربات فروشگاه روشن است!"

def run_web():
    web_app.run(host='0.0.0.0', port=5000, debug=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("📚 محصولات دیجیتال", callback_data="products")],
        [InlineKeyboardButton("🛒 سبد خرید (۰)", callback_data="cart")],
        [InlineKeyboardButton("💳 پرداخت", callback_data="payment")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="profile")]
    ]
    
    await update.message.reply_text(
        f"🛍️ به فروشگاه آموزشی خوش آمدید، {update.effective_user.first_name}!\n\n"
        "لطفاً گزینه مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 کتاب آموزشی پایتون - ۱۰۰,۰۰۰ تومان", callback_data="buy_book")],
        [InlineKeyboardButton("🎥 دوره ویدیویی تلگرام - ۲۰۰,۰۰۰ تومان", callback_data="buy_course")],
        [InlineKeyboardButton("📦 پکیج کامل - ۲۵۰,۰۰۰ تومان", callback_data="buy_package")],
        [InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main")]
    ]
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📚 محصولات دیجیتال:\n\n"
        "• کتاب آموزشی پایتون - ۱۰۰,۰۰۰ تومان\n"
        "• دوره ویدیویی تلگرام - ۲۰۰,۰۰۰ تومان\n"
        "• پکیج کامل - ۲۵۰,۰۰۰ تومان\n\n"
        "لطفاً محصول مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "products":
        await products_menu(update, context)
    
    elif query.data == "buy_book":
        # اضافه به سبد خرید
        if user_id not in user_data:
            user_data[user_id] = {"cart": [], "purchases": 0}
        user_data[user_id]["cart"].append("کتاب آموزشی پایتون - ۱۰۰,۰۰۰ تومان")
        
        await query.edit_message_text("✅ کتاب به سبد خرید اضافه شد!")
        await show_cart(update, context)
    
    elif query.data == "buy_course":
        await query.edit_message_text("🎥 دوره ویدیویی به زودی اضافه خواهد شد!")
    
    elif query.data == "buy_package":
        await query.edit_message_text("📦 پکیج کامل به زودی اضافه خواهد شد!")
    
    elif query.data == "cart":
        await show_cart(update, context)
    
    elif query.data == "payment":
        await process_payment(update, context)
    
    elif query.data == "support":
        await query.edit_message_text(
            "📞 پشتیبانی:\n\n"
            "برای ارتباط با پشتیبانی و پاسخ به سوالات:\n"
            "👤 @YourSupportUsername\n\n"
            "ساعات پاسخگویی: ۹ صبح تا ۶ عصر",
            parse_mode="Markdown"
        )
    
    elif query.data == "profile":
        user = query.from_user
        purchases = user_data.get(user_id, {}).get("purchases", 0)
        
        await query.edit_message_text(
            f"👤 حساب کاربری:\n\n"
            f"🆔 آیدی: {user.id}\n"
            f"👤 نام: {user.first_name}\n"
            f"📧 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
            f"🛍️ تعداد خریدها: {purchases}\n"
            f"⭐ وضعیت: کاربر عادی",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main")
            ]])
        )
    
    elif query.data == "back_main":
        await start_from_callback(update, context)
    
    elif query.data == "checkout":
        await finalize_payment(update, context)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    cart = user_data.get(user_id, {}).get("cart", [])
    
    if cart:
        total = len(cart) * 100000  # فرضی
        cart_text = "\n".join([f"• {item}" for item in cart])
        
        await query.edit_message_text(
            f"🛒 سبد خرید شما:\n\n{cart_text}\n\n"
            f"💰 جمع کل: {total:,} تومان\n\n"
            "لطفاً اقدام مورد نظر را انتخاب کنید:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💳 پرداخت نهایی", callback_data="checkout"),
                InlineKeyboardButton("🗑️ خالی کردن سبد", callback_data="clear_cart")
            ], [
                InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main")
            ]])
        )
    else:
        await query.edit_message_text(
            "🛒 سبد خرید شما خالی است!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📚 محصولات", callback_data="products"),
                InlineKeyboardButton("🔙 برگشت", callback_data="back_main")
            ]])
        )

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(
        "💳 درگاه پرداخت:\n\n"
        "در حال حاضر درگاه پرداخت تستی فعال است.\n"
        "برای تست ربات، از منوی محصولات یک آیتم انتخاب کنید.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📚 محصولات", callback_data="products"),
            InlineKeyboardButton("🔙 برگشت", callback_data="back_main")
        ]])
    )

async def finalize_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.edit_message_text("⏳ در حال انتقال به درگاه پرداخت (تست)...")
    
    # شبیه‌سازی پرداخت موفق
    await query.message.reply_text("✅ پرداخت موفق! (تست)\nفایل در حال ارسال...")
    
    try:
        with open(PDF_FILE, 'rb') as pdf:
            await query.message.reply_document(
                pdf, 
                caption="📖 کتاب آموزشی پایتون شما با موفقیت ارسال شد!\n\nممنون از خرید شما 💙"
            )
    except Exception as e:
        await query.message.reply_text(f"❌ خطا در ارسال فایل: {e}")
    
    # آپدیت اطلاعات کاربر
    if user_id not in user_data:
        user_data[user_id] = {"cart": [], "purchases": 0}
    user_data[user_id]["purchases"] += 1
    user_data[user_id]["cart"] = []
    
    # پیام به ادمین
    await context.bot.send_message(
        ADMIN_ID, 
        f"💰 خرید جدید!\n\n"
        f"👤 خریدار: {query.from_user.first_name}\n"
        f"🆔 آیدی: {user_id}\n"
        f"📧 یوزرنیم: @{query.from_user.username}\n"
        f"📦 محصول: کتاب آموزشی پایتون\n"
        f"💵 مبلغ: ۱۰۰,۰۰۰ تومان",
        parse_mode="Markdown"
    )

async def start_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    cart_count = len(user_data.get(user_id, {}).get("cart", []))
    
    keyboard = [
        [InlineKeyboardButton("📚 محصولات دیجیتال", callback_data="products")],
        [InlineKeyboardButton(f"🛒 سبد خرید ({cart_count})", callback_data="cart")],
        [InlineKeyboardButton("💳 پرداخت", callback_data="payment")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="profile")]
    ]
    
    await query.edit_message_text(
        f"🛍️ به فروشگاه آموزشی خوش آمدید، {query.from_user.first_name}!\n\n"
        "لطفاً گزینه مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ ربات فروشگاه با منوی کامل روشن شد!")
    application.run_polling()

if __name__ == "__main__":
    main()
        

