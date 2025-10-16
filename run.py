#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فایل اجرای ربات جنگ
Run script for war simulation bot
"""

import os
import sys
import subprocess
from datetime import datetime

def check_requirements():
    """بررسی وابستگی‌ها"""
    print("🔍 بررسی وابستگی‌ها...")
    
    try:
        import bale
        print("✅ کتابخانه بله نصب شده است")
    except ImportError:
        print("❌ کتابخانه بله نصب نشده است!")
        print("💡 برای نصب از دستور زیر استفاده کنید:")
        print("pip install bale-python")
        return False
    
    return True

def check_config():
    """بررسی فایل تنظیمات"""
    print("🔍 بررسی فایل تنظیمات...")
    
    if os.path.exists("config.py"):
        print("✅ فایل config.py موجود است")
        return True
    else:
        print("⚠️ فایل config.py موجود نیست!")
        print("💡 فایل config_example.py را کپی کرده و نام آن را به config.py تغییر دهید")
        print("💡 سپس توکن ربات خود را در آن قرار دهید")
        return False

def run_tests():
    """اجرای تست‌ها"""
    print("🧪 اجرای تست‌ها...")
    
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ تست‌ها موفق بود!")
            return True
        else:
            print("❌ تست‌ها ناموفق بود!")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ خطا در اجرای تست‌ها: {e}")
        return False

def main():
    """اجرای اصلی"""
    print("🚀 راه‌اندازی ربات شبیه‌سازی جنگ...")
    print("=" * 50)
    
    # بررسی وابستگی‌ها
    if not check_requirements():
        return
    
    print()
    
    # بررسی فایل تنظیمات
    if not check_config():
        print("\n💡 برای ادامه، لطفاً فایل config.py را ایجاد کنید")
        return
    
    print()
    
    # اجرای تست‌ها
    if not run_tests():
        print("\n💡 برای ادامه، لطفاً مشکلات تست را برطرف کنید")
        return
    
    print()
    print("=" * 50)
    print("🎉 همه چیز آماده است!")
    print("🚀 در حال راه‌اندازی ربات...")
    print("=" * 50)
    
    # اجرای ربات
    try:
        from war_simulation_bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n⏹️ ربات متوقف شد!")
    except Exception as e:
        print(f"\n❌ خطا در اجرای ربات: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()