# app/keyboards.py
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .locales import BTN_CANCEL, BTN_I_REJOINED, BTN_JOIN_CHANNEL, BTN_VERIFY_JOIN

# --- CallbackData Factories ---
class PaginatorCallback(CallbackData, prefix="pag"):
    action: str
    page: int

class SlugCallback(CallbackData, prefix="slug"):
    action: str
    slug_id: str

# --- Admin Panel Keyboards ---
def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="✨ Manage Slugs", callback_data="admin_manage_slugs")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast_start")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_slug_management_keyboard(slugs: list, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # THE FIX IS HERE: We define start_offset first, then end_offset.
    start_offset = page * page_size
    end_offset = start_offset + page_size
    
    for slug in slugs[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=f"📄 {slug['label']}", callback_data=SlugCallback(action="view", slug_id=slug['slug']).pack()))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=PaginatorCallback(action="prev", page=page).pack()))
    if end_offset < len(slugs):
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=PaginatorCallback(action="next", page=page).pack()))
    builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="➕ Add new slug", callback_data="admin_add_slug"))
    builder.row(InlineKeyboardButton(text="⬅️ Back to Admin Panel", callback_data="admin_panel_main"))
    return builder.as_markup()

def get_single_slug_keyboard(slug_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔄 Change file", callback_data=SlugCallback(action="edit_file", slug_id=slug_id).pack())],
        [InlineKeyboardButton(text="🗑️ Delete slug", callback_data=SlugCallback(action="delete", slug_id=slug_id).pack())],
        [InlineKeyboardButton(text="⬅️ Back to list", callback_data="admin_manage_slugs")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_slug_delete_confirm_keyboard(slug_id: str) -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text="✅ Yes, Delete", callback_data=SlugCallback(action="confirm_delete", slug_id=slug_id).pack()),
        InlineKeyboardButton(text="❌ No, Go Back", callback_data=SlugCallback(action="view", slug_id=slug_id).pack())
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    
def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text="🚀 Broadcast message", callback_data="broadcast_send"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="fsm_cancel"),
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- FSM & Generic Keyboards ---
def get_cancel_fsm_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=BTN_CANCEL, callback_data="fsm_cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- User-Facing Keyboards ---
def get_pre_verify_keyboard(invite_url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=BTN_JOIN_CHANNEL, url=invite_url)],
        [InlineKeyboardButton(text=BTN_VERIFY_JOIN, callback_data="verify_join")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_file_keyboard(slug: str, label: str) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=f"📄 {label}", callback_data=f"send:{slug}")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_rejoin_keyboard(invite_url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=BTN_JOIN_CHANNEL, url=invite_url)],
        [InlineKeyboardButton(text=BTN_I_REJOINED, callback_data="verify_join")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)