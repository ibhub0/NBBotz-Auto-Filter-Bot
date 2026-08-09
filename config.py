import os, re, time
import info

ID_PATTERN = re.compile(r"^-?\d+$")

def env(name, default=""):
    val = os.environ.get(name)
    if val is not None and val != "":
        return val.strip()
    return str(default) if default is not None else ""

def env_int(name, default):
    value = env(name, str(default))
    return int(value) if value else default

def clean_channel(value):
    if isinstance(value, list) and value:
        return str(value[0])
    return str(value).strip().lstrip("@") if value else ""

def parse_admins(value):
    if isinstance(value, list):
        return value
    return [int(admin) if ID_PATTERN.fullmatch(str(admin)) else admin for admin in str(value).split()]


class Settings:
    API_ID = env_int("API_ID", getattr(info, "API_ID", 0))
    API_HASH = env("API_HASH", getattr(info, "API_HASH", ""))
    BOT_TOKEN = env("BOT_TOKEN", getattr(info, "BOT_TOKEN", ""))
    
    pics_default = getattr(info, "NOR_IMG", "") or (getattr(info, "PICS", [""])[0] if isinstance(getattr(info, "PICS", None), list) else getattr(info, "PICS", ""))
    BOT_PIC = env("BOT_PIC", env("START_PIC", pics_default or "https://telegra.ph/file/21a8e96b45cd6ac4d3da6.jpg"))
    BOT_UPTIME = time.time()
    PORT = env_int("PORT", getattr(info, "PORT", 8089))
    WORKERS = env_int("WORKERS", getattr(info, "WORKERS", 200))
    
    auth_ch = getattr(info, "AUTH_CHANNEL", "")
    if isinstance(auth_ch, list) and auth_ch:
        auth_ch_str = str(auth_ch[0])
    else:
        auth_ch_str = str(auth_ch) if auth_ch else ""
    FORCE_SUB = clean_channel(env("FORCE_SUB", auth_ch_str))
    
    DB_NAME = env("DB_NAME", getattr(info, "DATABASE_NAME", "dreamxbotz_caption"))
    BOT_USERNAME = env("BOT_USERNAME", getattr(info, "SESSION_NAME", "DreamXbotz_caption"))
    CHANNEL_URL = env("CHANNEL_URL", getattr(info, "CHNL_LNK", "https://t.me/dreamxbotz"))
    SUPPORT_URL = env("SUPPORT_URL", getattr(info, "SUPPORT_CHAT", ""))
    SOURCE_URL = env("SOURCE_URL", getattr(info, "OWNER_LNK", ""))
    DB_URL = env("DB_URL", getattr(info, "DATABASE_URI", ""))
    LOG_LEVEL = env("LOG_LEVEL", "INFO").upper()
    DEF_CAP = env(
        "DEF_CAP",
        getattr(
            info,
            "CUSTOM_FILE_CAPTION",
            "<b>{file_name}</b>\n\n<b>Main Telegram Channel:</b> @dreamxbotz",
        ),
    )
    STICKER_ID = env(
        "STICKER_ID",
        "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE",
    )
    ADMINS = parse_admins(env("ADMINS", getattr(info, "ADMINS", [])))

    @classmethod
    def missing_required(cls):
        required = {
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "BOT_TOKEN": cls.BOT_TOKEN,
            "DB_URL": cls.DB_URL,
        }
        return [name for name, value in required.items() if not value]

    @classmethod
    def summary(cls):
        return {
            "bot": cls.BOT_USERNAME,
            "database": cls.DB_NAME,
            "force_sub": bool(cls.FORCE_SUB),
            "admins": len(cls.ADMINS),
            "workers": cls.WORKERS,
            "port": cls.PORT,
        }

DreamXbotz = Settings
