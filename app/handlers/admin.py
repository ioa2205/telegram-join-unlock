# app/handlers/admin.py
import asyncio
import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import Settings, load_config
from app.db import Database
from app.keyboards import (PaginatorCallback, SlugCallback, get_admin_panel_keyboard, get_broadcast_confirm_keyboard,
                           get_cancel_fsm_keyboard, get_single_slug_keyboard, get_slug_delete_confirm_keyboard,
                           get_slug_management_keyboard)
from app.locales import *
from app.services import analytics, broadcast, slugs
from app.states import AdminStates

log = logging.getLogger(__name__)
router = Router()
router.message.filter(F.from_user.id.in_(load_config().admin_ids))
router.callback_query.filter(F.from_user.id.in_(load_config().admin_ids))

@router.callback_query(F.data == "fsm_cancel")
async def fsm_cancel_handler(query: types.CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    await admin_panel_callback_handler(query, db)
    await query.answer(MSG_ACTION_CANCELLED)

async def show_main_admin_panel(message_or_query: types.Message | types.CallbackQuery, db: Database, edit: bool = False):
    stats_data = await analytics.get_stats(db)
    total_users, joined_users = stats_data['total_users'], stats_data['joined_users']
    conversion_rate = (joined_users / total_users * 100) if total_users > 0 else 0
    
    text = MSG_ADMIN_PANEL_GREETING_WITH_STATS.format(
        total_users=total_users, joined_users=joined_users, conversion_rate=conversion_rate
    )
    
    if edit and isinstance(message_or_query, types.CallbackQuery):
        await message_or_query.message.edit_text(text, reply_markup=get_admin_panel_keyboard())
    else:
        await message_or_query.answer(text, reply_markup=get_admin_panel_keyboard())

@router.message(Command("admin"))
async def admin_panel_handler(message: Message, db: Database):
    await show_main_admin_panel(message, db)

@router.callback_query(F.data == "admin_panel_main")
async def admin_panel_callback_handler(query: types.CallbackQuery, db: Database):
    await show_main_admin_panel(query, db, edit=True)

@router.callback_query(F.data == "admin_manage_slugs")
async def manage_slugs_handler(query: types.CallbackQuery, db: Database):
    all_slugs = await slugs.get_all_slugs(db)
    
    # Determine the text based on whether slugs exist
    text = MSG_SLUG_MANAGEMENT_TITLE
    if not all_slugs:
        text = MSG_SLUG_MANAGEMENT_EMPTY

    # Always show the management keyboard, even if the list is empty
    await query.message.edit_text(
        text,
        reply_markup=get_slug_management_keyboard(all_slugs)
    )

@router.callback_query(PaginatorCallback.filter())
async def slug_paginator_handler(query: types.CallbackQuery, callback_data: PaginatorCallback, db: Database):
    all_slugs = await slugs.get_all_slugs(db)
    new_page = callback_data.page
    if callback_data.action == "next": new_page += 1
    elif callback_data.action == "prev": new_page -= 1
    await query.message.edit_text(MSG_SLUG_MANAGEMENT_TITLE, reply_markup=get_slug_management_keyboard(all_slugs, page=new_page))

@router.callback_query(SlugCallback.filter(F.action == "view"))
async def view_slug_handler(query: types.CallbackQuery, callback_data: SlugCallback, db: Database):
    slug_data = await slugs.get_slug_data(db, callback_data.slug_id)
    if not slug_data:
        await query.answer("Slug not found.", show_alert=True); return
    perf_data = await analytics.get_slug_performance(db, callback_data.slug_id)
    starts, sends = perf_data['starts'], perf_data['sends']
    funnel_rate = (sends / starts * 100) if starts > 0 else 0
    text = MSG_SLUG_DETAILS_WITH_STATS.format(
        slug_id=slug_data['slug'], label=slug_data['label'],
        file_status='✅ Yes' if slug_data['file_id'] != 'MISSING' else '❌ No',
        starts=starts, verifies=perf_data['verifies'], sends=sends, funnel_rate=funnel_rate
    )
    await query.message.edit_text(text, reply_markup=get_single_slug_keyboard(callback_data.slug_id))

@router.callback_query(F.data == "admin_add_slug")
async def add_slug_start(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_slug_name)
    await query.message.edit_text(MSG_FSM_ADD_SLUG_NAME, reply_markup=get_cancel_fsm_keyboard())

@router.message(AdminStates.add_slug_name)
async def add_slug_name(message: Message, state: FSMContext, db: Database):
    if not slugs.is_valid_slug(message.text):
        await message.answer(MSG_FSM_ADD_SLUG_INVALID, reply_markup=get_cancel_fsm_keyboard())
        return
    if await slugs.get_slug_data(db, message.text):
        await message.answer(MSG_ADD_SLUG_FAIL.format(slug=message.text), reply_markup=get_cancel_fsm_keyboard())
        return
    await state.update_data(slug_name=message.text)
    await state.set_state(AdminStates.add_slug_label)
    await message.answer(MSG_FSM_ADD_SLUG_LABEL, reply_markup=get_cancel_fsm_keyboard())

@router.message(AdminStates.add_slug_label)
async def add_slug_label(message: Message, state: FSMContext):
    await state.update_data(slug_label=message.text)
    await state.set_state(AdminStates.add_slug_file)
    await message.answer(MSG_FSM_ADD_SLUG_FILE, reply_markup=get_cancel_fsm_keyboard())

@router.message(AdminStates.add_slug_file, F.document)
async def add_slug_file(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    slug_name, slug_label = data['slug_name'], data['slug_label']
    file_id = message.document.file_id
    query = "INSERT INTO slugs (slug, label, file_id, active) VALUES (?, ?, ?, 1)"
    await db.execute(query, (slug_name, slug_label, file_id))
    await state.clear()
    await message.answer(f"✅ Success! Slug `<code>{slug_name}</code>` has been created.")
    all_slugs = await slugs.get_all_slugs(db)
    await message.answer(MSG_SLUG_MANAGEMENT_TITLE, reply_markup=get_slug_management_keyboard(all_slugs))

@router.message(AdminStates.add_slug_file)
async def add_slug_file_incorrect(message: Message, state: FSMContext):
    await message.answer("Please send a document (file), not a photo or text.", reply_markup=get_cancel_fsm_keyboard())

@router.callback_query(SlugCallback.filter(F.action == "delete"))
async def delete_slug_confirm(query: types.CallbackQuery, callback_data: SlugCallback):
    await query.message.edit_text(f"Are you sure you want to delete `<code>{callback_data.slug_id}</code>`?", reply_markup=get_slug_delete_confirm_keyboard(callback_data.slug_id))

@router.callback_query(SlugCallback.filter(F.action == "confirm_delete"))
async def delete_slug_execute(query: types.CallbackQuery, callback_data: SlugCallback, db: Database):
    await db.execute("DELETE FROM slugs WHERE slug = ?", (callback_data.slug_id,))
    await query.answer("Slug deleted successfully!", show_alert=True)
    all_slugs = await slugs.get_all_slugs(db)
    await query.message.edit_text(MSG_SLUG_MANAGEMENT_TITLE, reply_markup=get_slug_management_keyboard(all_slugs))

@router.callback_query(F.data == "admin_broadcast_start")
async def broadcast_start(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcast_confirm)
    await query.message.edit_text(MSG_FSM_BROADCAST_CONTENT, reply_markup=get_cancel_fsm_keyboard())

@router.message(AdminStates.broadcast_confirm)
async def broadcast_content_received(message: Message, state: FSMContext):
    await state.update_data(broadcast_message=message)
    await message.copy_to(chat_id=message.chat.id)
    await message.answer(MSG_FSM_BROADCAST_CONFIRM, reply_markup=get_broadcast_confirm_keyboard())

@router.callback_query(F.data == "broadcast_send")
async def broadcast_send(query: types.CallbackQuery, state: FSMContext, bot: Bot, db: Database, config: Settings):
    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")
    if not broadcast_message:
        await state.clear()
        await query.message.edit_text("Error: Broadcast message not found.", reply_markup=get_admin_panel_keyboard())
        return
    await state.clear()
    all_chat_ids = await broadcast.get_all_chat_ids(db)
    if not all_chat_ids:
        await query.message.edit_text(MSG_BROADCAST_NO_USERS, reply_markup=get_admin_panel_keyboard())
        return
    await query.message.edit_text(MSG_BROADCAST_STARTED.format(user_count=len(all_chat_ids)))
    asyncio.create_task(broadcast.send_broadcast(bot=bot, db=db, from_chat_id=query.message.chat.id, message=broadcast_message, rate_limit_sec=config.rate_limit_broadcast_per_sec))

@router.message(Command("stats"))
async def stats_handler(message: types.Message, db: Database):
    stats_data = await analytics.get_stats(db)
    text = f"{MSG_STATS_HEADER}\n\n"
    text += f"👤 Total Users: {stats_data['total_users']}\n"
    text += f"✅ Verified Users: {stats_data['joined_users']}\n"
    text += f"🏃 30-Day Active: {stats_data['active_30d']}\n\n"
    text += "--- Per-Slug Stats ---\n"
    if not stats_data['per_slug']: text += "No slug activity yet."
    else:
        for item in stats_data['per_slug']:
            text += (f"🔹 <code>{item['slug']}</code> ({item['label']}):\n"
                     f"  Starts: {item['starts']}, Verified: {item['verifies']}, Sent: {item['sends']}\n")
    await message.answer(text)