import telebot
from telebot import types
import time
import random

# ----------------------------------------------------------------------
# ⚠️ 1. CONFIGURATION (ACTUAL LINKS REPLACED)
# ----------------------------------------------------------------------

BOT_TOKEN = "8567624597:AAHcPd3aLAgRi3ax6KxubQC815-P4_e1QIM"

# 1. Instagram Links (External links - User is trusted to click)
INSTAGRAM_GROUP_LINKS = [
    "https://ig.me/j/AbbPpB6xb9MBbt9N/", 
    "https://ig.me/j/AbbC8DSRGT_g0gxe/",
]

# 2. Telegram Channels (Verification REQUIRED - Bot must be ADMIN in these)
# KEY: The Channel Identifier (MUST be the @Username OR the negative Chat ID)
# VALUE: The permanent link/invite link for the button
TELEGRAM_CHANNELS_MAP = {
    # Public Channel (Key is the @username)
    "@stylify11": "https://t.me/stylify11", 
    
    # Private Channel IDs (Keys MUST be the actual negative Chat ID, e.g., '-1001230000002')
    # PLEASE REPLACE these placeholder keys with the actual IDs you retrieved.
    "@BACKUP402": "https://t.me/backup402",
    "-1003271030135": "https://t.me/+BtVKpn8atmw2M2I9",
    "-1003465742298": "https://t.me/+aPJSYoDLAkQwYjc9",
}

# 3. Final Reward Link
FINAL_CHANNEL_LINK = "https://t.me/+qRXQ-sAuykZiMGE1" 

# ----------------------------------------------------------------------
# 2. BOT CORE FUNCTIONS
# ----------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

def is_member(chat_id, user_id):
    """Checks if a user is an active member in a Telegram chat."""
    try:
        # Bot MUST be an admin for this method to check membership
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        # User not found in chat, usually means not joined or bot lacks permissions
        return False

def check_telegram_channels(user_id):
    """Checks if the user is a member of ALL required Telegram channels."""
    for channel_id, channel_link in TELEGRAM_CHANNELS_MAP.items():
        if not is_member(channel_id, user_id):
            # --- START DIAGNOSTIC PRINT ---
            print("==================================================")
            print(f"!!! VERIFICATION FAILED !!!")
            print(f"User ID: {user_id}")
            print(f"Failing Channel Key (ID used in code): {channel_id}")
            print(f"Failing Channel Link (Button URL): {channel_link}")
            print("==================================================")
            # --- END DIAGNOSTIC PRINT ---
            return False, channel_link 
    return True, None # All Telegram checks passed All Telegram checks passed

# ----------------------------------------------------------------------
# 3. HANDLERS
# ----------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command, displaying all required links."""
    
    markup = types.InlineKeyboardMarkup()
    
    # 1. Instagram Buttons
    for i, link in enumerate(INSTAGRAM_GROUP_LINKS):
        markup.add(types.InlineKeyboardButton(f"📸 Join Insta Group {i+1}", url=link))

    # 2. Telegram Channel Buttons
    for i, link in enumerate(TELEGRAM_CHANNELS_MAP.values()):
        markup.add(types.InlineKeyboardButton(f"📢 Join Channel {i+1}", url=link))
    
    # Add the final check button
    markup.add(types.InlineKeyboardButton("✅ I Have Joined All", callback_data='check_membership'))

    bot.send_message(
        message.chat.id, 
        "Welcome! Please Join by clicking the buttons to complete all **2 Instagram** and **4 Telegram** requirements, then click **'I Have Joined All'** to proceed.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == 'check_membership')
def callback_check_membership(call):
    """Handles the 'I Have Joined All' button click."""
    
    user_id = call.from_user.id
    # missing_link will be the URL of the first channel the user hasn't joined
    all_telegram_joined, missing_link = check_telegram_channels(user_id) 

    if all_telegram_joined:
        # Success: All Telegram channels joined
        final_markup = types.InlineKeyboardMarkup()
        final_markup.add(types.InlineKeyboardButton("🎉 Get Final Channel Link", url=FINAL_CHANNEL_LINK))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"**Congratulations!** All requirements met. Here is your exclusive reward link:",
            reply_markup=final_markup,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "Reward unlocked!")
        
    else:
        # Failure: User missed a Telegram channel.
        retry_markup = types.InlineKeyboardMarkup()
        
        # ADDED BACK: The button that links directly to the missing channel
        retry_markup.add(types.InlineKeyboardButton("Join Missing Channel", url=missing_link))
        
        # The Retry button
        retry_markup.add(types.InlineKeyboardButton("✅ I Have Joined All (Retry)", callback_data='check_membership'))

        # FIX FOR ERROR 400: Generate a unique ID to prevent repeat errors
        unique_id = f"{int(time.time())}{random.randint(1000, 9999)}"
        unique_suffix = f"\n\n\u200b" 

        failure_text = "❌ **Verification Failed!**\n\nPlease ensure you have joined all 4 Telegram channels. Click below to join the channel you missed, then try again." + unique_suffix
        
        # Use a try...except block to handle the 'message not modified' gracefully
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=failure_text,
                reply_markup=retry_markup,
                parse_mode="Markdown"
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e):
                 pass # Silently ignore the error
             else:
                 raise e 
        
        # Include the unique_id in the callback answer to make it unique across rapid clicks
        bot.answer_callback_query(call.id, text=f"Still missing channels. Retry: {unique_id}", show_alert=True)

# ----------------------------------------------------------------------
# 4. RUN THE BOT
# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("Bot is starting and polling for updates...")
    bot.infinity_polling()