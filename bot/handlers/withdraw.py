"""Withdraw flow using FSM (amount → method → account → name → confirm)."""
from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import keyboards, texts
from ..config import settings
from ..db import SessionLocal
from ..services.user_service import get_user_by_id, get_user_by_telegram_id
from ..services.withdraw_service import WithdrawError, create_request

router = Router(name="withdraw")


class WithdrawStates(StatesGroup):
    amount = State()
    method = State()
    account = State()
    name = State()
    confirm = State()


@router.message(F.text == texts.MENU_BUTTON_WITHDRAW)
async def on_withdraw_start(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Ketik /start dulu.")
            return
        if user.balance < settings.min_withdraw:
            await message.answer(
                texts.WITHDRAW_TOO_LOW.format(
                    min_amount=texts.fmt_rp(settings.min_withdraw),
                    balance=texts.fmt_rp(user.balance),
                )
            )
            return
        balance = user.balance

    await state.set_state(WithdrawStates.amount)
    await message.answer(
        texts.WITHDRAW_ASK_AMOUNT.format(
            balance=texts.fmt_rp(balance),
            min_amount=texts.fmt_rp(settings.min_withdraw),
            max_amount=texts.fmt_rp(settings.max_withdraw),
        )
    )


@router.message(Command("cancel"), StateFilter(WithdrawStates))
@router.message(F.text == texts.BTN_CANCEL, StateFilter(WithdrawStates))
async def cancel_flow(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.WITHDRAW_CANCELLED, reply_markup=keyboards.main_menu())


@router.message(WithdrawStates.amount)
async def on_amount(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip().replace(".", "").replace(",", "")
    if not raw.isdigit():
        await message.answer(texts.WITHDRAW_INVALID_AMOUNT)
        return
    amount = int(raw)
    if amount < settings.min_withdraw:
        await message.answer(
            f"❌ Minimum <b>{texts.fmt_rp(settings.min_withdraw)}</b>. Coba lagi:"
        )
        return
    if amount > settings.max_withdraw:
        await message.answer(
            f"❌ Maksimum <b>{texts.fmt_rp(settings.max_withdraw)}</b> per request. "
            "Coba lagi:"
        )
        return
    if message.from_user is None:
        return
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user is None or user.balance < amount:
            await state.clear()
            await message.answer("Saldo tidak cukup. Batal.")
            return

    await state.update_data(amount=amount)
    await state.set_state(WithdrawStates.method)
    await message.answer(
        texts.WITHDRAW_ASK_METHOD, reply_markup=keyboards.withdraw_methods()
    )


@router.callback_query(WithdrawStates.method, F.data.startswith("wd_method:"))
async def on_method(query: CallbackQuery, state: FSMContext) -> None:
    if query.data is None:
        await query.answer()
        return
    method = query.data.split(":", 1)[1]
    if method not in settings.payout_methods:
        await query.answer("Metode tidak valid", show_alert=True)
        return
    await state.update_data(method=method)
    await state.set_state(WithdrawStates.account)
    if isinstance(query.message, Message):
        await query.message.answer(texts.WITHDRAW_ASK_ACCOUNT.format(method=method))
    await query.answer()


@router.callback_query(F.data == "wd_cancel")
async def on_cancel_cb(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if isinstance(query.message, Message):
        await query.message.answer(
            texts.WITHDRAW_CANCELLED, reply_markup=keyboards.main_menu()
        )
    await query.answer()


@router.message(WithdrawStates.account)
async def on_account(message: Message, state: FSMContext) -> None:
    account = (message.text or "").strip()
    if len(account) < 6 or len(account) > 60:
        await message.answer("Nomor akun tidak valid. Coba lagi:")
        return
    data = await state.get_data()
    await state.update_data(account_number=account)
    await state.set_state(WithdrawStates.name)
    await message.answer(texts.WITHDRAW_ASK_NAME.format(method=data.get("method", "")))


@router.message(WithdrawStates.name)
async def on_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer("Nama tidak valid. Coba lagi:")
        return
    await state.update_data(account_name=name)
    data = await state.get_data()

    await state.set_state(WithdrawStates.confirm)
    await message.answer(
        texts.WITHDRAW_CONFIRM.format(
            amount=texts.fmt_rp(data["amount"]),
            method=data["method"],
            account_number=data["account_number"],
            account_name=data["account_name"],
        ),
        reply_markup=keyboards.withdraw_confirm(),
    )


@router.callback_query(WithdrawStates.confirm, F.data == "wd_confirm")
async def on_confirm(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if query.from_user is None:
        await query.answer()
        return
    data = await state.get_data()
    await state.clear()

    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, query.from_user.id)
        if user is None:
            await query.answer("Akun tidak ditemukan", show_alert=True)
            return
        try:
            req = await create_request(
                session,
                user,
                amount=int(data["amount"]),
                method=str(data["method"]),
                account_number=str(data["account_number"]),
                account_name=str(data["account_name"]),
            )
        except WithdrawError as exc:
            await session.rollback()
            await query.answer(f"Gagal: {exc}", show_alert=True)
            return
        await session.commit()
        wid = req.id
        amount = req.amount
        method = req.method
        account_number = req.account_number
        account_name = req.account_name
        user_telegram_id = user.telegram_id
        username = user.username
        first_name = user.first_name

    if isinstance(query.message, Message):
        await query.message.answer(
            texts.WITHDRAW_SUBMITTED.format(
                wid=wid, amount=texts.fmt_rp(amount)
            ),
            reply_markup=keyboards.main_menu(),
        )
    await query.answer()

    # Notify all admins
    notify = (
        f"🆕 <b>Withdraw Request #{wid}</b>\n\n"
        f"User: {first_name or '-'} "
        f"({'@' + username if username else 'no_username'}, "
        f"<code>{user_telegram_id}</code>)\n"
        f"Nominal: <b>{texts.fmt_rp(amount)}</b>\n"
        f"Metode: {method}\n"
        f"No: <code>{account_number}</code>\n"
        f"Nama: {account_name}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                notify,
                reply_markup=keyboards.admin_withdraw_actions(wid),
            )
        except Exception:
            pass


_ = get_user_by_id  # silence unused import linter
