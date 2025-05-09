import telebot
from telebot import types
import uuid

TOKEN = '7824210014:AAH6PRpQFan9GmrtRHGiXQV2rf0RL70mkhQ'
CHANNEL_USERNAME = "@comic_nub"

bot = telebot.TeleBot(TOKEN)

# دیتابیس فایل‌ها
files_db = {}
# دیتابیس لینک‌ها
links_db = {}

# بررسی عضویت در کانال
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        bot.send_message(user_id, "خوش آمدید! شما عضو کانال هستید. فایل‌های مورد نظر را ارسال کنید.")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

@bot.message_handler(content_types=['photo', 'document', 'video'])
def handle_file(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
            elif message.document:
                file_id = message.document.file_id
            elif message.video:
                file_id = message.video.file_id

            # ذخیره فایل‌ها در دیتابیس
            file_uuid = str(uuid.uuid4())  # شناسه منحصر به فرد برای فایل
            files_db[file_uuid] = {
                'type': message.content_type,
                'file_id': file_id,
                'user_id': user_id
            }

            # ایجاد لینک منحصر به فرد
            file_link = f"http://yourserver.com/file/{file_uuid}"  # لینک منحصر به فرد
            links_db[file_uuid] = {
                'user_id': user_id,
                'file_id': file_id
            }

            bot.send_message(user_id, f"فایل شما ذخیره شد. لینک دانلود فایل: {file_link}")
        except Exception as e:
            bot.send_message(user_id, "در هنگام ذخیره فایل مشکلی پیش آمد.")
            print(f"Error handling file: {e}")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

# دریافت فایل با لینک منحصر به فرد
@bot.message_handler(commands=['download'])
def download_file(message):
    # لینک شامل شناسه فایل است که بعد از /file/ در URL آمده
    link_parts = message.text.split(" ")
    if len(link_parts) > 1:
        file_uuid = link_parts[1].strip()  # گرفتن شناسه از لینک
        if file_uuid in links_db:
            file_data = links_db[file_uuid]
            if file_data['user_id'] == message.from_user.id:
                # ارسال فایل به کاربر
                file_id = file_data['file_id']
                if files_db[file_uuid]['type'] == 'photo':
                    bot.send_photo(message.from_user.id, file_id)
                elif files_db[file_uuid]['type'] == 'document':
                    bot.send_document(message.from_user.id, file_id)
                elif files_db[file_uuid]['type'] == 'video':
                    bot.send_video(message.from_user.id, file_id)
            else:
                bot.send_message(message.from_user.id, "شما مجوز دسترسی به این فایل را ندارید.")
        else:
            bot.send_message(message.from_user.id, "لینک وارد شده صحیح نیست.")
    else:
        bot.send_message(message.from_user.id, "لینک دریافت فایل را ارسال کنید.")

bot.polling(none_stop=True)
