# فایل نمونه تنظیمات ربات جنگ
# این فایل را کپی کرده و نام آن را به config.py تغییر دهید

# توکن ربات بله
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# تنظیمات بازی
GAME_CONFIG = {
    # فاصله زمانی تولید منابع (دقیقه)
    "RESOURCE_PRODUCTION_INTERVAL": 5,
    
    # حداکثر سطح کشور
    "MAX_COUNTRY_LEVEL": 50,
    
    # حداکثر تعداد لاگ‌ها
    "MAX_LOGS": 10000,
    
    # حداقل قدرت برای حمله
    "MIN_ATTACK_POWER": 100,
    
    # حداکثر اختلاف سطح برای حمله
    "MAX_LEVEL_DIFF_FOR_ATTACK": 2,
    
    # شانس فتح کشور (درصد)
    "CONQUEST_CHANCE_BASE": 10,
    
    # شانس موفقیت جاسوسی (درصد)
    "SPY_SUCCESS_BASE": 30,
}

# تنظیمات لاگ
LOG_CONFIG = {
    "ENABLE_FILE_LOGGING": True,
    "LOG_FILE": "war_logs.txt",
    "LOG_LEVEL": "INFO"
}

# تنظیمات پایگاه داده
DATABASE_CONFIG = {
    "DATA_FILE": "war_data.txt",
    "BACKUP_INTERVAL": 3600,  # ثانیه
    "MAX_BACKUPS": 5
}