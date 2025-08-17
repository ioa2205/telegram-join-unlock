# app/locales.py

# --- User-facing strings ---
MSG_START_PRE_VERIFY_WITH_SLUG = """
Assalomu alaykum, {user_name}!

Siz <b>"{slug_label}"</b> uchun keldingiz. Uni ochish uchun, iltimos, avval guruhga qo‘shiling va "✅ A’zo bo‘ldim" tugmasini bosing.
"""
MSG_START_NO_PAYLOAD = "Kechirasiz, siz foydalangan havola xato yoki muddati o'tgan. Iltimos, havolani olgan joyingizdan qayta tekshirib ko'ring."
MSG_VERIFY_FAIL = "Siz hali guruhga a’zo emassiz. Iltimos, qo‘shiling va yana tekshiring."
MSG_VERIFIED_SUCCESS = "Tabriklaymiz! Siz tanlagan material tayyor."
MSG_LEFT_CHANNEL = "Ko‘rinishidan guruhga a’zolik bekor qilingan. Iltimos, qayta qo‘shiling."

# --- User Buttons ---
BTN_JOIN_CHANNEL = "🔗 Guruhga qo‘shilish"
BTN_VERIFY_JOIN = "✅ A’zo bo‘ldim"
BTN_I_REJOINED = "✅ Qayta a'zo bo'ldim"

# --- Admin Panel ---
MSG_ADMIN_PANEL_GREETING_WITH_STATS = """
Welcome to the Admin Panel.

<b>📊 At-a-Glance:</b>
• <b>Total Users:</b> {total_users}
• <b>Verified Members:</b> {joined_users} ({conversion_rate:.1f}%)

What would you like to do?
"""
BTN_CANCEL = "❌ Cancel"
MSG_ACTION_CANCELLED = "Action cancelled."
MSG_SLUG_MANAGEMENT_TITLE = "Select a slug to manage:"
MSG_SLUG_MANAGEMENT_EMPTY = "No slugs have been configured yet. Add your first one below."
MSG_SLUG_DETAILS_WITH_STATS = """
📄 <b>Slug Details</b>

• <b>ID:</b> <code>{slug_id}</code>
• <b>Label:</b> {label}
• <b>File Set:</b> {file_status}

<b>📈 Performance:</b>
• <b>Starts:</b> {starts}
• <b>Verifications:</b> {verifies}
• <b>Files Sent:</b> {sends}
• <b>Funnel Conversion Rate:</b> {funnel_rate:.1f}%
"""
# --- Admin FSM & Broadcast ---
MSG_FSM_ADD_SLUG_NAME = "1/3: Enter the unique slug ID (e.g., `ielts_speaking`). Use only lowercase letters, numbers, and underscores."
MSG_FSM_ADD_SLUG_INVALID = "❌ Invalid format. Please use only lowercase letters (a-z), numbers (0-9), and underscores (_), 2-50 characters long."
MSG_FSM_ADD_SLUG_LABEL = "2/3: Enter the button label that users will see (e.g., `IELTS Speaking Pack`)."
MSG_FSM_ADD_SLUG_FILE = "3/3: Now, please send the document/file for this slug."
MSG_FSM_BROADCAST_CONTENT = "Send the message you want to broadcast to all users. It can be text, a photo, a video, or a document."
MSG_FSM_BROADCAST_CONFIRM = "This is a preview of your broadcast message. Are you sure you want to send this to all users?"
MSG_BROADCAST_STARTED = "✅ Broadcast started for {user_count} users. You will receive a summary message when it is complete."
MSG_BROADCAST_NO_USERS = "❌ There are no users to broadcast to."
MSG_ADD_SLUG_FAIL = "❌ A slug with the name `<code>{slug}</code>` already exists."
MSG_STATS_HEADER = "📊 Bot Statistics"

# --- Bot Command Descriptions ---
CMD_START = "Start the bot and get your file"
CMD_ADMIN = "Open the admin control panel"
CMD_STATS = "View bot statistics"