import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import Settings
from DreamXbotz.helpers.caption_tools import media_file_name, render_template, validate_template
from DreamXbotz.helpers.logging_setup import get_logger
from DreamXbotz.storage import (
    add_audit_log,
    delete_channel_caption,
    get_channel_caption,
    get_channel_stats,
    increment_channel_stat,
    save_channel_caption,
)
from DreamXbotz.helpers.telegram import flood_wait_seconds

LOGGER = get_logger("plugins.auto_caption")
SAMPLE_FILE_NAME = "Movie 2026 Hindi 1080p"
SAMPLE_CAPTION = "Original upload caption"


async def delete_messages(m1, m2):
    await asyncio.sleep(5)
    for m in (m1, m2):
        try:
            if m:
                await m.delete()
        except Exception:
            pass


@Client.on_message(filters.command("set_caption") & filters.channel)
async def set_caption(bot, message):
    if len(message.command) < 2:
        rep = await message.reply(
            "Usage:\n"
            "<code>/set_caption {file_name}</code>\n\n"
            "Available placeholders: <code>{file_name}</code>, <code>{caption}</code>, "
            "<code>{language}</code>, <code>{year}</code>, <code>{quality}</code>, <code>{file_size}</code>, <code>{duration}</code>, <code>{season}</code>, <code>{episode}</code>"
        )
        asyncio.create_task(delete_messages(message, rep))
        return

    caption = message.text.split(" ", 1)[1].strip()
    is_valid, invalid_fields = validate_template(caption)
    if not is_valid:
        rep = await message.reply(
            f"Unknown placeholder(s): <code>{invalid_fields}</code>\n\n"
            "Use only allowed placeholders."
        )
        asyncio.create_task(delete_messages(message, rep))
        return

    await save_channel_caption(message.chat.id, caption)
    await add_audit_log(
        "caption_saved",
        message.chat.id,
        actor_id=getattr(message.from_user, "id", None),
        detail={"caption": caption},
    )
    rep = await message.reply(f"Caption saved successfully.\n\nNew caption:\n<code>{caption}</code>")
    asyncio.create_task(delete_messages(message, rep))


@Client.on_message(filters.command("caption_preview") & filters.channel)
async def caption_preview(bot, message):
    template = message.text.split(" ", 1)[1].strip() if len(message.command) > 1 else None
    if not template:
        caption_doc = await get_channel_caption(message.chat.id)
        template = caption_doc["caption"] if caption_doc else Settings.DEF_CAP

    is_valid, invalid_fields = validate_template(template)
    if not is_valid:
        rep = await message.reply(f"Template error: <code>{invalid_fields}</code>")
        asyncio.create_task(delete_messages(message, rep))
        return

    preview = render_template(template, None, SAMPLE_FILE_NAME, SAMPLE_CAPTION)
    rep = await message.reply(f"<b>Caption preview</b>\n\n{preview}")
    asyncio.create_task(delete_messages(message, rep))


@Client.on_message(filters.command("caption_vars") & filters.channel)
async def caption_vars(bot, message):
    rep = await message.reply(
        "<b>Available caption placeholders</b>\n\n"
        "<code>{file_name}</code> - cleaned file name\n"
        "<code>{caption}</code> - original caption or file name\n"
        "<code>{language}</code> - detected language\n"
        "<code>{year}</code> - detected release year\n"
        "<code>{quality}</code> - video quality (e.g., 1080p, 4K)\n"
        "<code>{file_size}</code> - media file size\n"
        "<code>{duration}</code> - media duration\n"
        "<code>{season}</code> - season number (e.g., S01)\n"
        "<code>{episode}</code> - episode number (e.g., E01)"
    )
    asyncio.create_task(delete_messages(message, rep))


@Client.on_message(filters.command("channel_stats") & filters.channel)
async def channel_stats(bot, message):
    stats = await get_channel_stats(message.chat.id)
    rep = await message.reply(
        "<b>Channel stats</b>\n\n"
        f"<b>Caption edits:</b> <code>{stats.get('caption_edits', 0)}</code>"
    )
    asyncio.create_task(delete_messages(message, rep))


@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def del_caption(_, message):
    result = await delete_channel_caption(message.chat.id)
    if result.deleted_count:
        await add_audit_log(
            "caption_deleted",
            message.chat.id,
            actor_id=getattr(message.from_user, "id", None),
        )
        rep = await message.reply("Custom caption deleted. I will use the default caption from now on.")
    else:
        rep = await message.reply("No custom caption was set for this channel.")
    asyncio.create_task(delete_messages(message, rep))


async def auto_edit_caption(bot, message):
    """Automatically edit media caption when posted in channels if configured."""
    file_name = media_file_name(message)
    if not file_name:
        return

    caption_doc = await get_channel_caption(message.chat.id)
    template = caption_doc["caption"] if caption_doc else Settings.DEF_CAP

    try:
        new_caption = render_template(template, message, file_name, message.caption)
        if message.caption != new_caption:
            await message.edit_caption(new_caption)
            await increment_channel_stat(message.chat.id, "caption_edits")
    except FloodWait as e:
        await asyncio.sleep(flood_wait_seconds(e))
        await message.edit_caption(render_template(template, message, file_name, message.caption))
    except KeyError as exc:
        LOGGER.warning("Caption template fallback for channel %s: %s", message.chat.id, exc)
        await message.edit_caption(render_template(Settings.DEF_CAP, message, file_name, message.caption))
    except Exception as exc:
        LOGGER.warning("Could not edit caption in channel %s: %s", message.chat.id, exc)
