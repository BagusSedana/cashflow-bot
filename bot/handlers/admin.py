"""Admin commands: stats, list/approve/reject withdraw, broadcast, ban, set rate."""
from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from .. import keyboards, texts
from ..config import settings
from ..db import (
    Earning,
    EarnSource,
    SessionLocal,
    User,
    WithdrawRequest,
    WithdrawStatus,
)
from ..services.user_service import get_user_by_id, get_user_by_telegram_id
from ..services.withdraw_service import (
    WithdrawError,
    approve,
    list_pending,
    mark_paid,
    reject,
)

router = Router(name="admin")


def _is_admin(user_id: int | None) -> bool:
    return user_id is not None and user_id in settings.admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    await message.answer(
        "🛠 <b>Panel Admin</b>\n\n"
        "/stats — statistik bot\n"
        "/pending — list withdraw pending\n"
        "/user &lt;telegram_id&gt; — info user\n"
        "/ban &lt;telegram_id&gt; — banned user\n"
        "/unban &lt;telegram_id&gt; — unbanned user\n"
        "/give &lt;telegram_id&gt; &lt;amount&gt; — kasih bonus saldo\n"
        "/broadcast &lt;pesan&gt; — kirim pesan ke semua user\n"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    async with SessionLocal() as session:
        total_users = (
            await session.execute(select(func.count(User.id)))
        ).scalar() or 0
        total_balance = (
            await session.execute(select(func.coalesce(func.sum(User.balance), 0)))
        ).scalar() or 0
        total_earned = (
            await session.execute(
                select(func.coalesce(func.sum(User.total_earned), 0))
            )
        ).scalar() or 0
        total_withdrawn = (
            await session.execute(
                select(func.coalesce(func.sum(User.total_withdrawn), 0))
            )
        ).scalar() or 0
        pending = (
            await session.execute(
                select(func.count(WithdrawRequest.id)).where(
                    WithdrawRequest.status == WithdrawStatus.PENDING.value
                )
            )
        ).scalar() or 0
        ad_views = (
            await session.execute(
                select(func.coalesce(func.sum(User.ads_watched), 0))
            )
        ).scalar() or 0

    await message.answer(
        "📊 <b>Statistik Bot</b>\n\n"
        f"Total user      : <b>{total_users}</b>\n"
        f"Total iklan     : <b>{ad_views}</b>\n"
        f"Total saldo aktif: <b>{texts.fmt_rp(int(total_balance))}</b>\n"
        f"Total earned    : <b>{texts.fmt_rp(int(total_earned))}</b>\n"
        f"Total withdrawn : <b>{texts.fmt_rp(int(total_withdrawn))}</b>\n"
        f"Withdraw pending: <b>{pending}</b>"
    )


@router.message(Command("pending"))
async def cmd_pending(message: Message) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    async with SessionLocal() as session:
        items = await list_pending(session, limit=20)
        if not items:
            await message.answer("Tidak ada withdraw pending.")
            return
        for req in items:
            user = await get_user_by_id(session, req.user_id)
            uname = (
                f"@{user.username}" if user and user.username else f"id:{user.telegram_id if user else '?'}"
            )
            text = (
                f"<b>#{req.id}</b> — {texts.fmt_rp(req.amount)} via {req.method}\n"
                f"User: {uname}\n"
                f"No: <code>{req.account_number}</code>\n"
                f"Nama: {req.account_name}\n"
                f"Dibuat: {req.created_at:%Y-%m-%d %H:%M}"
            )
            await message.answer(
                text, reply_markup=keyboards.admin_withdraw_actions(req.id)
            )


@router.message(Command("user"))
async def cmd_user(message: Message, command: CommandObject) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Format: /user &lt;telegram_id&gt;")
        return
    tg_id = int(command.args.strip())
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            await message.answer("User tidak ditemukan.")
            return
        await message.answer(
            f"<b>User #{user.id}</b>\n"
            f"TG: <code>{user.telegram_id}</code> "
            f"({'@' + user.username if user.username else 'no_username'})\n"
            f"Nama: {user.first_name}\n"
            f"Saldo: <b>{texts.fmt_rp(user.balance)}</b>\n"
            f"Total earned: {texts.fmt_rp(user.total_earned)}\n"
            f"Total withdrawn: {texts.fmt_rp(user.total_withdrawn)}\n"
            f"Iklan: {user.ads_watched}\n"
            f"Banned: {user.is_banned}\n"
            f"Daftar: {user.created_at:%Y-%m-%d %H:%M}"
        )


@router.message(Command("ban"))
async def cmd_ban(message: Message, command: CommandObject) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Format: /ban &lt;telegram_id&gt;")
        return
    tg_id = int(command.args.strip())
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            await message.answer("User tidak ditemukan.")
            return
        user.is_banned = True
        await session.commit()
    await message.answer(f"User <code>{tg_id}</code> di-ban.")


@router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Format: /unban &lt;telegram_id&gt;")
        return
    tg_id = int(command.args.strip())
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            await message.answer("User tidak ditemukan.")
            return
        user.is_banned = False
        await session.commit()
    await message.answer(f"User <code>{tg_id}</code> di-unban.")


@router.message(Command("give"))
async def cmd_give(message: Message, command: CommandObject) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].lstrip("-").isdigit():
        await message.answer("Format: /give &lt;telegram_id&gt; &lt;amount&gt;")
        return
    tg_id, amount = int(parts[0]), int(parts[1])
    async with SessionLocal() as session:
        user = await get_user_by_telegram_id(session, tg_id)
        if user is None:
            await message.answer("User tidak ditemukan.")
            return
        user.balance += amount
        if amount > 0:
            user.total_earned += amount
            session.add(
                Earning(
                    user_id=user.id,
                    amount=amount,
                    source=EarnSource.BONUS.value,
                    note="manual admin grant",
                )
            )
        await session.commit()
    await message.answer(
        f"Saldo user <code>{tg_id}</code> ditambah {texts.fmt_rp(amount)}."
    )


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: CommandObject, bot: Bot) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None):
        return
    text = command.args
    if not text:
        await message.answer("Format: /broadcast &lt;pesan&gt;")
        return
    sent = 0
    failed = 0
    async with SessionLocal() as session:
        result = await session.execute(select(User.telegram_id).where(User.is_banned.is_(False)))
        ids = [row[0] for row in result.all()]
    for tg_id in ids:
        try:
            await bot.send_message(tg_id, text)
            sent += 1
        except Exception:
            failed += 1
    await message.answer(f"📢 Broadcast selesai. Terkirim: {sent}, gagal: {failed}.")


# ---------- Inline button handlers ----------


async def _notify_user(bot: Bot, telegram_id: int, text: str) -> None:
    try:
        await bot.send_message(telegram_id, text)
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_wd_ok:"))
async def cb_approve(query: CallbackQuery, bot: Bot) -> None:
    if not _is_admin(query.from_user.id if query.from_user else None):
        await query.answer("Bukan admin", show_alert=True)
        return
    if not query.data:
        await query.answer()
        return
    wid = int(query.data.split(":", 1)[1])
    async with SessionLocal() as session:
        req = await session.get(WithdrawRequest, wid)
        if req is None:
            await query.answer("Request tidak ditemukan", show_alert=True)
            return
        try:
            await approve(session, req)
        except WithdrawError as exc:
            await query.answer(str(exc), show_alert=True)
            return
        await session.commit()
        user = await get_user_by_id(session, req.user_id)
        target = user.telegram_id if user else None
        amount = req.amount

    await query.answer("Disetujui ✅")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(
            reply_markup=keyboards.admin_withdraw_actions(wid)
        )
    if target is not None:
        await _notify_user(
            bot,
            target,
            texts.WITHDRAW_NOTIFY_USER_APPROVED.format(
                wid=wid, amount=texts.fmt_rp(amount)
            ),
        )


@router.callback_query(F.data.startswith("adm_wd_no:"))
async def cb_reject(query: CallbackQuery, bot: Bot) -> None:
    if not _is_admin(query.from_user.id if query.from_user else None):
        await query.answer("Bukan admin", show_alert=True)
        return
    if not query.data:
        await query.answer()
        return
    wid = int(query.data.split(":", 1)[1])
    reason = "Data tidak valid / mencurigai pelanggaran aturan."
    async with SessionLocal() as session:
        req = await session.get(WithdrawRequest, wid)
        if req is None:
            await query.answer("Request tidak ditemukan", show_alert=True)
            return
        try:
            await reject(session, req, reason)
        except WithdrawError as exc:
            await query.answer(str(exc), show_alert=True)
            return
        await session.commit()
        user = await get_user_by_id(session, req.user_id)
        target = user.telegram_id if user else None

    await query.answer("Ditolak (saldo dikembalikan) ❌")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
    if target is not None:
        await _notify_user(
            bot,
            target,
            texts.WITHDRAW_NOTIFY_USER_REJECTED.format(wid=wid, reason=reason),
        )


@router.callback_query(F.data.startswith("adm_wd_paid:"))
async def cb_paid(query: CallbackQuery, bot: Bot) -> None:
    if not _is_admin(query.from_user.id if query.from_user else None):
        await query.answer("Bukan admin", show_alert=True)
        return
    if not query.data:
        await query.answer()
        return
    wid = int(query.data.split(":", 1)[1])
    async with SessionLocal() as session:
        req = await session.get(WithdrawRequest, wid)
        if req is None:
            await query.answer("Request tidak ditemukan", show_alert=True)
            return
        try:
            await mark_paid(session, req)
        except WithdrawError as exc:
            await query.answer(str(exc), show_alert=True)
            return
        await session.commit()
        user = await get_user_by_id(session, req.user_id)
        target = user.telegram_id if user else None
        snapshot = (
            req.id,
            req.amount,
            req.method,
            req.account_number,
            req.account_name,
        )

    await query.answer("Ditandai sudah dibayar 💸")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
    if target is not None:
        wid_, amount_, method_, account_number_, account_name_ = snapshot
        await _notify_user(
            bot,
            target,
            texts.WITHDRAW_NOTIFY_USER_PAID.format(
                wid=wid_,
                amount=texts.fmt_rp(amount_),
                method=method_,
                account_number=account_number_,
                account_name=account_name_,
            ),
        )

    # Auto-post proof to channel if configured
    if settings.proof_channel_username:
        try:
            await bot.send_message(
                f"@{settings.proof_channel_username}",
                f"💸 <b>Bukti Pembayaran #{snapshot[0]}</b>\n\n"
                f"Nominal: <b>{texts.fmt_rp(snapshot[1])}</b>\n"
                f"Metode : {snapshot[2]}\n"
                f"Status : <b>SUDAH DIBAYAR</b> ✅",
            )
        except Exception:
            pass
