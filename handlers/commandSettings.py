import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    CALLBACK_CAMPUS_NOVOSIBIRSK,
    CALLBACK_CHOOSE_ACTIVE,
    CALLBACK_CHOOSE_INACTIVE,
    CALLBACK_CHOOSE_KAZAN,
    CALLBACK_CHOOSE_MOSCOW,
    CALLBACK_CHOOSE_NOVOSIBIRSK,
    CALLBACK_CHOOSE_OFFLINE,
    CALLBACK_CHOOSE_ONLINE,
    CALLBACK_ONLINE_NO,
    CALLBACK_ONLINE_YES,
    KEY_AUTHORIZED,
)
from telegram import ext as telegram_ext
from utils.getters import get_active_status, get_campus_name, get_online_status
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


async def settings_choose_campus(ctx: telegram_ext.CallbackContext, id: int) -> None:
    kbd = [
        [
            telegram.InlineKeyboardButton(
                get_campus_name(campus_slug),
                callback_data=callback_data,
            ),
        ]
        for [campus_slug, callback_data] in [
            [CALLBACK_CAMPUS_KAZAN, CALLBACK_CHOOSE_KAZAN],
            [CALLBACK_CAMPUS_MOSCOW, CALLBACK_CHOOSE_MOSCOW],
            [CALLBACK_CAMPUS_NOVOSIBIRSK, CALLBACK_CHOOSE_NOVOSIBIRSK],
        ]
    ]

    await ctx.bot.send_message(
        id,
        text="Если встреча будет оффлайн, то в каком кампусе?",
        reply_markup=telegram.InlineKeyboardMarkup(kbd),
    )


async def settings_choose_online(ctx: telegram_ext.CallbackContext, id: int) -> None:
    kbd = [
        [
            telegram.InlineKeyboardButton(
                get_online_status(online_slug),
                callback_data=callback_data,
            ),
        ]
        for [online_slug, callback_data] in [
            [CALLBACK_ONLINE_YES, CALLBACK_CHOOSE_ONLINE],
            [CALLBACK_ONLINE_NO, CALLBACK_CHOOSE_OFFLINE],
        ]
    ]

    await ctx.bot.send_message(
        id,
        text="Онлайн или оффлайн?\n\n"
        "Учти, что последний пир без пары из оффлайна, если таковой будет, будет сматчен с пиром из онлайна. "
        "Последний пир без из онлайна, если таковой будет, так и останется таковым.",
        reply_markup=telegram.InlineKeyboardMarkup(kbd),
    )


async def settings_choose_active(ctx: telegram_ext.CallbackContext, id: int) -> None:
    kbd = [
        [
            telegram.InlineKeyboardButton(
                get_active_status(active_slug),
                callback_data=callback_data,
            ),
        ]
        for [active_slug, callback_data] in [
            [CALLBACK_ACTIVE_YES, CALLBACK_CHOOSE_ACTIVE],
            [CALLBACK_ACTIVE_NO, CALLBACK_CHOOSE_INACTIVE],
        ]
    ]

    await ctx.bot.send_message(
        id,
        text="На этой неделе участвуешь в случайном кофе?",
        reply_markup=telegram.InlineKeyboardMarkup(kbd),
    )


async def settings_finish(ctx: telegram_ext.CallbackContext, id: int) -> None:
    await ctx.bot.send_message(
        id,
        text="Я запомнил твои предпочтения!\n\nУчти, что они автоматически продляются на все последующие недели, "
        "если ты их не изменишь.",
    )


async def handler_command_settings(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if not ctx.user_data.get(KEY_AUTHORIZED, False):
        await upd.message.reply_text(COMMAND_DENIED_NOT_AUTHORIZED)
        return

    await settings_choose_campus(ctx, upd.effective_user.id)
