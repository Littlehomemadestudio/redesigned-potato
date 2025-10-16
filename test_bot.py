#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فایل تست ربات جنگ
Test file for war simulation bot
"""

import json
import os
from datetime import datetime

def test_data_loading():
    """تست بارگذاری داده‌ها"""
    print("🧪 تست بارگذاری داده‌ها...")
    
    # ایجاد داده‌های تست
    test_data = {
        "users": {},
        "countries": {},
        "alliances": {},
        "battles": [],
        "logs": []
    }
    
    # ذخیره داده‌های تست
    with open("test_data.txt", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # بارگذاری داده‌ها
    with open("test_data.txt", 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    assert loaded_data == test_data
    print("✅ تست بارگذاری داده‌ها موفق!")
    
    # پاکسازی
    os.remove("test_data.txt")

def test_military_units():
    """تست واحدهای نظامی"""
    print("🧪 تست واحدهای نظامی...")
    
    # بارگذاری واحدهای نظامی از فایل اصلی
    from war_simulation_bot import MILITARY_UNITS
    
    # بررسی تعداد واحدها
    unit_count = len(MILITARY_UNITS)
    print(f"📊 تعداد واحدهای نظامی: {unit_count}")
    
    # بررسی دسته‌بندی‌ها
    categories = set()
    for unit in MILITARY_UNITS.values():
        categories.add(unit["category"])
    
    print(f"📊 دسته‌بندی‌ها: {len(categories)}")
    for category in sorted(categories):
        count = sum(1 for unit in MILITARY_UNITS.values() if unit["category"] == category)
        print(f"  • {category}: {count} واحد")
    
    assert unit_count >= 120, f"تعداد واحدها باید حداقل 120 باشد، اما {unit_count} است"
    print("✅ تست واحدهای نظامی موفق!")

def test_resources():
    """تست منابع"""
    print("🧪 تست منابع...")
    
    from war_simulation_bot import RESOURCES
    
    # بررسی منابع
    resource_count = len(RESOURCES)
    print(f"📊 تعداد منابع: {resource_count}")
    
    for resource, info in RESOURCES.items():
        assert "name" in info, f"منبع {resource} نام ندارد"
        assert "emoji" in info, f"منبع {resource} ایموجی ندارد"
        assert "base_income" in info, f"منبع {resource} درآمد پایه ندارد"
        print(f"  • {info['emoji']} {info['name']}: {info['base_income']}")
    
    print("✅ تست منابع موفق!")

def test_capital_upgrades():
    """تست اپگریدهای پایتخت"""
    print("🧪 تست اپگریدهای پایتخت...")
    
    from war_simulation_bot import CAPITAL_UPGRADES
    
    # بررسی اپگریدها
    upgrade_count = len(CAPITAL_UPGRADES)
    print(f"📊 تعداد اپگریدها: {upgrade_count}")
    
    for upgrade, info in CAPITAL_UPGRADES.items():
        assert "name" in info, f"اپگرید {upgrade} نام ندارد"
        assert "levels" in info, f"اپگرید {upgrade} سطح ندارد"
        assert "cost_multiplier" in info, f"اپگرید {upgrade} ضریب هزینه ندارد"
        assert "benefits" in info, f"اپگرید {upgrade} مزایا ندارد"
        print(f"  • {info['name']}: {info['levels']} سطح, {len(info['benefits'])} مزیت")
    
    print("✅ تست اپگریدهای پایتخت موفق!")

def test_user_data_structure():
    """تست ساختار داده کاربر"""
    print("🧪 تست ساختار داده کاربر...")
    
    from war_simulation_bot import get_user_data, RESOURCES, CAPITAL_UPGRADES
    
    # ایجاد داده کاربر تست
    user_data = get_user_data("test_chat", "test_user")
    
    # بررسی فیلدهای اصلی
    required_fields = [
        "level", "experience", "resources", "military", "capital",
        "battles_won", "battles_lost", "territory_conquered", "alliance",
        "achievements", "research", "diplomacy", "spies", "intelligence"
    ]
    
    for field in required_fields:
        assert field in user_data, f"فیلد {field} در داده کاربر وجود ندارد"
    
    # بررسی منابع
    for resource in RESOURCES:
        assert resource in user_data["resources"], f"منبع {resource} در داده کاربر وجود ندارد"
    
    # بررسی اپگریدها
    for upgrade in CAPITAL_UPGRADES:
        assert upgrade in user_data["capital"], f"اپگرید {upgrade} در داده کاربر وجود ندارد"
    
    print("✅ تست ساختار داده کاربر موفق!")

def main():
    """اجرای تمام تست‌ها"""
    print("🚀 شروع تست‌های ربات جنگ...")
    print("=" * 50)
    
    try:
        test_data_loading()
        print()
        
        test_military_units()
        print()
        
        test_resources()
        print()
        
        test_capital_upgrades()
        print()
        
        test_user_data_structure()
        print()
        
        print("=" * 50)
        print("🎉 تمام تست‌ها موفق بود!")
        print("✅ ربات آماده اجرا است!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()