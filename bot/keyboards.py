"""Reply / inline keyboard builders."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from . import texts
from .config import settings


def main_menu() -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(text=texts.MENU_BUTTON_EARN),
            KeyboardButton(text=texts.MENU_BUTTON_DAILY),
        ],
        [
            KeyboardButton(text=texts.MENU_BUTTON_BALANCE),
            KeyboardButton(text=texts.MENU_BUTTON_REFERRAL),
        ],
        [
            KeyboardButton(text=texts.MENU_BUTTON_WITHDRAW),
            KeyboardButton(text=texts.MENU_BUTTON_TASKS),
        ],
        [
            KeyboardButton(text=texts.MENU_BUTTON_HELP),
        ],
    ]
    if settings.proof_channel_username:
        rows[-1].append(KeyboardButton(text=texts.MENU_BUTTON_PROOF))
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def watch_again() -> InlineKeyboardMarkup:
    if settings.webapp_url:
        first_row = [
            InlineKeyboardButton(
                text="🎬 Tonton Lagi", web_app=WebAppInfo(url=settings.webapp_url)
            )
        ]
    else:
        first_row = [InlineKeyboardButton(text="🎬 Tonton Lagi", callback_data="watch_ad")]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            first_row,
            [InlineKeyboardButton(text="💰 Lihat Saldo", callback_data="show_balance")],
        ]
    )


def watch_button() -> InlineKeyboardMarkup:
    """Either a Mini App launch button (when WEBAPP_URL is set) or a callback fallback."""
    if settings.webapp_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="▶️ Buka Mini App & Tonton",
                        web_app=WebAppInfo(url=settings.webapp_url),
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Mulai Tonton Iklan", callback_data="watch_ad")],
        ]
    )


def withdraw_methods() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=m, callback_data=f"wd_method:{m}")]
        for m in settings.payout_methods
    ]
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="wd_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def withdraw_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=texts.BTN_CONFIRM, callback_data="wd_confirm"),
                InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="wd_cancel"),
            ]
        ]
    )


def admin_withdraw_actions(wid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Setujui", callback_data=f"adm_wd_ok:{wid}"),
                InlineKeyboardButton(text="❌ Tolak", callback_data=f"adm_wd_no:{wid}"),
            ],
            [
                InlineKeyboardButton(
                    text="💸 Tandai Sudah Bayar", callback_data=f"adm_wd_paid:{wid}"
                ),
            ],
        ]
    )
