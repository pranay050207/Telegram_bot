import telebot
from telebot import types
import time
import random
import json
import os

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------

BOT_TOKEN = "8567624597:AAHcPd3aLAgRi3ax6KxubQC815-P4_e1QIM"   # <-- Your Token Added

ADMIN_ID = 8077675422                 # Your admin ID
LOG_GROUP_ID = -5074122337            # Private group for auto logs

INSTAGRAM_GROUP_LINKS = [
    "https://ig.me/j/AbbPpB6xb9MBbt9N/",
    "https://ig.me/j/AbbC8DSRGT_g0gxe/"
]

TELEGRAM_CHANNELS_MAP = {
    "@stylify11": "https://t.me/stylify11",
    "@BACKUP402": "https://t.me/BACKUP402",
    "-1003271030135": "https://t.me/+BtVKpn8atmw2M2I9",
    "-1003465742298": "https://t.me/+aPJSYoDLAkQwYjc9"
}

FINAL_CHANNEL_LINK = "https://t.me/+qRXQ-sAuykZiMGE1"

# ----------------------------------------------------------------------
# 2. AUTO USER LOGGING
# ----------------------------------------------------------------------

USER_LOG = "user_log.json"

def log_user(message):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "phone": None,
        "timestamp": time.time()
    }

    if os.path.exists(USER_LOG):
        with open(USER_LOG, "r") as f:
            users = json.load(f)
    else:
        users = {}

    users[str(message.from_user.id)] = user_data

    with open(USER_LOG, "w") as f:
        json.dump(users, f, indent=4)

    log_text = (
        "📥 *NEW USER STARTED BOT*\n\n"
        f"👤 *Name:* {message.from_user.first_name or ''} {message.from_user.last_name or ''}\n"
        f"🔗 *Username:* @{message.from_user.username}\n"
        f"🆔 *User ID:* `{message.from_user.id}`\n"
        f"📱 *Phone:* None\n"
        f"⏰ *Joined:* {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        bot.send_message(LOG_GROUP_ID, log_text, parse_mode="Markdown")
    except Exception as e:
        print("Error sending log:", e)

# ----------------------------------------------------------------------
# 3. BROADCAST USER STORAGE
# ----------------------------------------------------------------------

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

users_list = load_users()

# ----------------------------------------------------------------------
# 4. BOT INITIALIZATION
# ----------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

def is_member(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

def check_telegram_channels(user_id):
    for channel_id, channel_link in TELEGRAM_CHANNELS_MAP.items():
        if not is_member(channel_id, user_id):
            return False, channel_link
    return True, None

# ----------------------------------------------------------------------
# 5. START COMMAND
# ----------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):

    log_user(message)

    user_id = message.from_user.id
    if user_id not in users_list:
        users_list.append(user_id)
        save_users(users_list)

    markup = types.InlineKeyboardMarkup()

    for i, link in enumerate(INSTAGRAM_GROUP_LINKS):
        markup.add(types.InlineKeyboardButton(f"📸 Join Insta Group {i+1}", url=link))

    for i, link in enumerate(TELEGRAM_CHANNELS_MAP.values()):
        markup.add(types.InlineKeyboardButton(f"📢 Join Channel {i+1}", url=link))

    markup.add(types.InlineKeyboardButton("✅ I Have Joined All", callback_data='check_membership'))

    bot.send_message(
        message.chat.id,
        "Welcome! Join all groups and channels, then tap **I Have Joined All**.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ----------------------------------------------------------------------
# 6. MEMBERSHIP VERIFICATION
# ----------------------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data == 'check_membership')
def callback_check_membership(call):

    user_id = call.from_user.id
    all_joined, missing_link = check_telegram_channels(user_id)

    if all_joined:
        final_markup = types.InlineKeyboardMarkup()
        final_markup.add(types.InlineKeyboardButton("🎉 Get Final Link", url=FINAL_CHANNEL_LINK))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🎉 **You completed all steps. Here is your final link:**",
            reply_markup=final_markup,
            parse_mode="Markdown"
        )
    else:
        retry_markup = types.InlineKeyboardMarkup()
        retry_markup.add(types.InlineKeyboardButton("Join Missing Channel", url=missing_link))
        retry_markup.add(types.InlineKeyboardButton("🔁 Retry Verification", callback_data='check_membership'))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ You missed a channel! Join and retry.",
            reply_markup=retry_markup,
            parse_mode="Markdown"
        )

# ----------------------------------------------------------------------
# 7. BROADCAST SYSTEM (ADMIN ONLY)
# ----------------------------------------------------------------------

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized.")
        return

    if message.reply_to_message:
        media = message.reply_to_message
        sent = 0

        for uid in users_list:
            try:
                if media.photo:
                    bot.send_photo(uid, media.photo[-1].file_id, caption=media.caption)
                elif media.video:
                    bot.send_video(uid, media.video.file_id, caption=media.caption)
                else:
                    bot.send_message(uid, media.text)
                sent += 1
            except:
                pass

        bot.reply_to(message, f"📢 Media broadcast sent to {sent} users.")
        return

    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "❗ Use: /broadcast your message OR reply to media.")
        return

    sent = 0
    for uid in users_list:
        try:
            bot.send_message(uid, text)
            sent += 1
        except:
            pass

    bot.reply_to(message, f"📢 Broadcast sent to {sent} users.")

# ----------------------------------------------------------------------
# 8. RUN BOT
# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("Bot is running with auto-logging + broadcast…")
    bot.infinity_polling()
