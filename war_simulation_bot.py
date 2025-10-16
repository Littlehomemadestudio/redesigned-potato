#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات شبیه‌سازی جنگ پیشرفته برای بله
War Simulation Bot - Advanced Military Strategy Game for Bale
"""

import os
import json
import time
import random
import asyncio
import traceback
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from bale import Bot, Message, User, Chat, ChatMember, InlineKeyboard, InlineKeyboardButton, MenuKeyboardButton, MenuKeyboardMarkup

# ==================== CONFIGURATION ====================
# تلاش برای بارگذاری تنظیمات از فایل config.py
try:
    from config import BOT_TOKEN, GAME_CONFIG, LOG_CONFIG, DATABASE_CONFIG
    TOKEN = BOT_TOKEN
    DATA_FILE = DATABASE_CONFIG.get("DATA_FILE", "war_data.txt")
    LOG_FILE = LOG_CONFIG.get("LOG_FILE", "war_logs.txt")
except ImportError:
    # استفاده از تنظیمات پیش‌فرض
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # توکن ربات خود را اینجا قرار دهید
    DATA_FILE = "war_data.txt"
    LOG_FILE = "war_logs.txt"
    GAME_CONFIG = {
        "RESOURCE_PRODUCTION_INTERVAL": 5,
        "MAX_COUNTRY_LEVEL": 50,
        "MAX_LOGS": 10000,
        "MIN_ATTACK_POWER": 100,
        "MAX_LEVEL_DIFF_FOR_ATTACK": 2,
        "CONQUEST_CHANCE_BASE": 10,
        "SPY_SUCCESS_BASE": 30,
    }

# Initialize bot
bot = Bot(token=TOKEN)

# ==================== GAME CONFIGURATION ====================

# Military Units Database - 120+ units
MILITARY_UNITS = {
    # === INFANTRY ===
    "soldier": {"name": "سرباز", "cost": 10, "power": 5, "category": "infantry", "emoji": "🪖", "level_req": 1},
    "marine": {"name": "تفنگدار دریایی", "cost": 25, "power": 12, "category": "infantry", "emoji": "🪖", "level_req": 2},
    "special_forces": {"name": "نیروی ویژه", "cost": 50, "power": 25, "category": "infantry", "emoji": "🪖", "level_req": 3},
    "sniper": {"name": "تک‌تیرانداز", "cost": 30, "power": 18, "category": "infantry", "emoji": "🎯", "level_req": 2},
    "engineer": {"name": "مهندس نظامی", "cost": 40, "power": 15, "category": "infantry", "emoji": "🔧", "level_req": 2},
    "medic": {"name": "پزشک نظامی", "cost": 35, "power": 10, "category": "infantry", "emoji": "⚕️", "level_req": 2},
    "paratrooper": {"name": "چترباز", "cost": 60, "power": 22, "category": "infantry", "emoji": "🪂", "level_req": 3},
    "commando": {"name": "کماندو", "cost": 80, "power": 35, "category": "infantry", "emoji": "⚔️", "level_req": 4},
    
    # === LIGHT VEHICLES ===
    "jeep": {"name": "جیپ نظامی", "cost": 100, "power": 20, "category": "light_vehicle", "emoji": "🚙", "level_req": 1},
    "humvee": {"name": "هموی", "cost": 150, "power": 30, "category": "light_vehicle", "emoji": "🚗", "level_req": 2},
    "armored_car": {"name": "خودرو زرهی", "cost": 200, "power": 40, "category": "light_vehicle", "emoji": "🚐", "level_req": 2},
    "recon_vehicle": {"name": "خودرو شناسایی", "cost": 180, "power": 35, "category": "light_vehicle", "emoji": "🔍", "level_req": 2},
    "mrap": {"name": "خودرو ضد مین", "cost": 300, "power": 50, "category": "light_vehicle", "emoji": "🛡️", "level_req": 3},
    
    # === TANKS ===
    "light_tank": {"name": "تانک سبک", "cost": 500, "power": 80, "category": "tank", "emoji": "🚗", "level_req": 2},
    "medium_tank": {"name": "تانک متوسط", "cost": 800, "power": 120, "category": "tank", "emoji": "🚗", "level_req": 3},
    "heavy_tank": {"name": "تانک سنگین", "cost": 1200, "power": 180, "category": "tank", "emoji": "🚗", "level_req": 4},
    "mbt": {"name": "تانک اصلی نبرد", "cost": 2000, "power": 300, "category": "tank", "emoji": "🚗", "level_req": 5},
    "abrams": {"name": "آبرامز M1A2", "cost": 3000, "power": 450, "category": "tank", "emoji": "🚗", "level_req": 6},
    "leopard": {"name": "لئوپارد 2A7", "cost": 3200, "power": 480, "category": "tank", "emoji": "🚗", "level_req": 6},
    "t90": {"name": "تی-90", "cost": 2800, "power": 420, "category": "tank", "emoji": "🚗", "level_req": 6},
    "challenger": {"name": "چلنجر 2", "cost": 3500, "power": 500, "category": "tank", "emoji": "🚗", "level_req": 7},
    "armata": {"name": "آرماتا T-14", "cost": 4000, "power": 600, "category": "tank", "emoji": "🚗", "level_req": 8},
    
    # === ARTILLERY ===
    "mortar": {"name": "خمپاره", "cost": 200, "power": 60, "category": "artillery", "emoji": "💣", "level_req": 2},
    "howitzer": {"name": "توپخانه", "cost": 600, "power": 150, "category": "artillery", "emoji": "💣", "level_req": 3},
    "mlrs": {"name": "سامانه راکت انداز", "cost": 1000, "power": 250, "category": "artillery", "emoji": "🚀", "level_req": 4},
    "railgun": {"name": "توپ ریل", "cost": 5000, "power": 800, "category": "artillery", "emoji": "⚡", "level_req": 8},
    "himears": {"name": "هایمارز", "cost": 1500, "power": 300, "category": "artillery", "emoji": "🚀", "level_req": 5},
    "pzh2000": {"name": "پی‌زد 2000", "cost": 2000, "power": 400, "category": "artillery", "emoji": "💣", "level_req": 6},
    
    # === ANTI-AIR ===
    "stinger": {"name": "استینگر", "cost": 300, "power": 40, "category": "anti_air", "emoji": "🚀", "level_req": 2},
    "patriot": {"name": "پاتریوت", "cost": 2000, "power": 200, "category": "anti_air", "emoji": "🛡️", "level_req": 5},
    "s400": {"name": "اس-400", "cost": 3000, "power": 300, "category": "anti_air", "emoji": "🛡️", "level_req": 6},
    "iron_dome": {"name": "گنبد آهنی", "cost": 1500, "power": 150, "category": "anti_air", "emoji": "🛡️", "level_req": 4},
    "thad": {"name": "تاد", "cost": 4000, "power": 500, "category": "anti_air", "emoji": "🛡️", "level_req": 7},
    
    # === FIGHTER AIRCRAFT ===
    "f16": {"name": "اف-16", "cost": 2000, "power": 200, "category": "fighter", "emoji": "✈️", "level_req": 3},
    "f22": {"name": "اف-22 رپتور", "cost": 5000, "power": 500, "category": "fighter", "emoji": "✈️", "level_req": 6},
    "f35": {"name": "اف-35", "cost": 6000, "power": 600, "category": "fighter", "emoji": "✈️", "level_req": 7},
    "su27": {"name": "سو-27", "cost": 3000, "power": 300, "category": "fighter", "emoji": "✈️", "level_req": 4},
    "su35": {"name": "سو-35", "cost": 4000, "power": 400, "category": "fighter", "emoji": "✈️", "level_req": 5},
    "su57": {"name": "سو-57", "cost": 7000, "power": 700, "category": "fighter", "emoji": "✈️", "level_req": 8},
    "j20": {"name": "جی-20", "cost": 5500, "power": 550, "category": "fighter", "emoji": "✈️", "level_req": 7},
    "eurofighter": {"name": "یوروفایتر", "cost": 3500, "power": 350, "category": "fighter", "emoji": "✈️", "level_req": 5},
    "rafale": {"name": "رافال", "cost": 3800, "power": 380, "category": "fighter", "emoji": "✈️", "level_req": 5},
    "gripen": {"name": "گریپن", "cost": 2500, "power": 250, "category": "fighter", "emoji": "✈️", "level_req": 4},
    
    # === BOMBERS ===
    "b52": {"name": "بی-52", "cost": 4000, "power": 400, "category": "bomber", "emoji": "✈️", "level_req": 5},
    "b1": {"name": "بی-1 لنسر", "cost": 5000, "power": 500, "category": "bomber", "emoji": "✈️", "level_req": 6},
    "b2": {"name": "بی-2 اسپیریت", "cost": 8000, "power": 800, "category": "bomber", "emoji": "✈️", "level_req": 8},
    "tu95": {"name": "تو-95", "cost": 3500, "power": 350, "category": "bomber", "emoji": "✈️", "level_req": 5},
    "tu160": {"name": "تو-160", "cost": 6000, "power": 600, "category": "bomber", "emoji": "✈️", "level_req": 7},
    "tu22m": {"name": "تو-22M", "cost": 4500, "power": 450, "category": "bomber", "emoji": "✈️", "level_req": 6},
    
    # === HELICOPTERS ===
    "apache": {"name": "آپاچی", "cost": 1500, "power": 150, "category": "helicopter", "emoji": "🚁", "level_req": 3},
    "black_hawk": {"name": "بلک هاوک", "cost": 1200, "power": 120, "category": "helicopter", "emoji": "🚁", "level_req": 3},
    "chinook": {"name": "چینوک", "cost": 1000, "power": 100, "category": "helicopter", "emoji": "🚁", "level_req": 2},
    "mi24": {"name": "می-24", "cost": 1800, "power": 180, "category": "helicopter", "emoji": "🚁", "level_req": 4},
    "mi28": {"name": "می-28", "cost": 2000, "power": 200, "category": "helicopter", "emoji": "🚁", "level_req": 4},
    "ka52": {"name": "کا-52", "cost": 2200, "power": 220, "category": "helicopter", "emoji": "🚁", "level_req": 5},
    "tiger": {"name": "تیگر", "cost": 2500, "power": 250, "category": "helicopter", "emoji": "🚁", "level_req": 5},
    
    # === DRONES ===
    "predator": {"name": "پردیتور", "cost": 800, "power": 80, "category": "drone", "emoji": "🚁", "level_req": 2},
    "reaper": {"name": "ریپر", "cost": 1200, "power": 120, "category": "drone", "emoji": "🚁", "level_req": 3},
    "global_hawk": {"name": "گلوبال هاوک", "cost": 2000, "power": 200, "category": "drone", "emoji": "🚁", "level_req": 4},
    "bayraktar": {"name": "بیرق‌دار", "cost": 600, "power": 60, "category": "drone", "emoji": "🚁", "level_req": 2},
    "shahed": {"name": "شاهد", "cost": 400, "power": 40, "category": "drone", "emoji": "🚁", "level_req": 1},
    "switchblade": {"name": "سوئیچ‌بلید", "cost": 300, "power": 30, "category": "drone", "emoji": "🚁", "level_req": 1},
    "kamikaze": {"name": "کامیکازه", "cost": 200, "power": 20, "category": "drone", "emoji": "💥", "level_req": 1},
    
    # === NAVAL SHIPS ===
    "patrol_boat": {"name": "قایق گشت", "cost": 500, "power": 50, "category": "naval", "emoji": "🚤", "level_req": 2},
    "corvette": {"name": "کوروت", "cost": 1500, "power": 150, "category": "naval", "emoji": "🚢", "level_req": 3},
    "frigate": {"name": "فرگیت", "cost": 3000, "power": 300, "category": "naval", "emoji": "🚢", "level_req": 4},
    "destroyer": {"name": "ناوشکن", "cost": 5000, "power": 500, "category": "naval", "emoji": "🚢", "level_req": 5},
    "cruiser": {"name": "کروزر", "cost": 8000, "power": 800, "category": "naval", "emoji": "🚢", "level_req": 6},
    "battleship": {"name": "ناو جنگی", "cost": 12000, "power": 1200, "category": "naval", "emoji": "🚢", "level_req": 7},
    "aircraft_carrier": {"name": "ناو هواپیمابر", "cost": 25000, "power": 2500, "category": "naval", "emoji": "🚢", "level_req": 8},
    "submarine": {"name": "زیردریایی", "cost": 6000, "power": 600, "category": "naval", "emoji": "🛳️", "level_req": 5},
    "nuclear_sub": {"name": "زیردریایی هسته‌ای", "cost": 15000, "power": 1500, "category": "naval", "emoji": "🛳️", "level_req": 7},
    "littoral": {"name": "ناو ساحلی", "cost": 2000, "power": 200, "category": "naval", "emoji": "🚢", "level_req": 3},
    
    # === MISSILES ===
    "hellfire": {"name": "هلفایر", "cost": 200, "power": 100, "category": "missile", "emoji": "🚀", "level_req": 2},
    "tomahawk": {"name": "توماهوک", "cost": 1000, "power": 500, "category": "missile", "emoji": "🚀", "level_req": 4},
    "scud": {"name": "اسکاد", "cost": 800, "power": 400, "category": "missile", "emoji": "🚀", "level_req": 3},
    "patriot_missile": {"name": "موشک پاتریوت", "cost": 500, "power": 250, "category": "missile", "emoji": "🚀", "level_req": 3},
    "s400_missile": {"name": "موشک اس-400", "cost": 600, "power": 300, "category": "missile", "emoji": "🚀", "level_req": 4},
    "icbm": {"name": "موشک بالستیک قاره‌ای", "cost": 5000, "power": 2000, "category": "missile", "emoji": "🚀", "level_req": 8},
    "cruise": {"name": "موشک کروز", "cost": 1200, "power": 600, "category": "missile", "emoji": "🚀", "level_req": 4},
    "ballistic": {"name": "موشک بالستیک", "cost": 2000, "power": 1000, "category": "missile", "emoji": "🚀", "level_req": 5},
    "hypersonic": {"name": "موشک فراصوت", "cost": 3000, "power": 1500, "category": "missile", "emoji": "🚀", "level_req": 6},
    "nuclear_missile": {"name": "موشک هسته‌ای", "cost": 10000, "power": 5000, "category": "missile", "emoji": "☢️", "level_req": 9},
    
    # === SPECIAL WEAPONS ===
    "laser_weapon": {"name": "سلاح لیزری", "cost": 8000, "power": 1000, "category": "special", "emoji": "⚡", "level_req": 8},
    "railgun": {"name": "توپ ریل", "cost": 6000, "power": 800, "category": "special", "emoji": "⚡", "level_req": 7},
    "plasma_weapon": {"name": "سلاح پلاسما", "cost": 12000, "power": 1500, "category": "special", "emoji": "⚡", "level_req": 9},
    "nuclear_bomb": {"name": "بمب هسته‌ای", "cost": 15000, "power": 3000, "category": "special", "emoji": "☢️", "level_req": 9},
    "hydrogen_bomb": {"name": "بمب هیدروژنی", "cost": 25000, "power": 5000, "category": "special", "emoji": "☢️", "level_req": 10},
    "neutron_bomb": {"name": "بمب نوترونی", "cost": 20000, "power": 4000, "category": "special", "emoji": "☢️", "level_req": 9},
    "emp_weapon": {"name": "سلاح الکترومغناطیسی", "cost": 10000, "power": 2000, "category": "special", "emoji": "⚡", "level_req": 8},
    "chemical_weapon": {"name": "سلاح شیمیایی", "cost": 5000, "power": 1000, "category": "special", "emoji": "☠️", "level_req": 6},
    "biological_weapon": {"name": "سلاح بیولوژیکی", "cost": 8000, "power": 1500, "category": "special", "emoji": "🦠", "level_req": 7},
    "cyber_weapon": {"name": "سلاح سایبری", "cost": 3000, "power": 500, "category": "special", "emoji": "💻", "level_req": 5},
    
    # === DEFENSE SYSTEMS ===
    "bunker": {"name": "پناهگاه", "cost": 1000, "power": 200, "category": "defense", "emoji": "🏰", "level_req": 3},
    "fortress": {"name": "قلعه", "cost": 3000, "power": 600, "category": "defense", "emoji": "🏰", "level_req": 5},
    "wall": {"name": "دیوار دفاعی", "cost": 500, "power": 100, "category": "defense", "emoji": "🧱", "level_req": 2},
    "minefield": {"name": "میدان مین", "cost": 300, "power": 50, "category": "defense", "emoji": "💣", "level_req": 1},
    "radar": {"name": "رادار", "cost": 800, "power": 0, "category": "defense", "emoji": "📡", "level_req": 2},
    "sonar": {"name": "سونار", "cost": 600, "power": 0, "category": "defense", "emoji": "📡", "level_req": 2},
    "satellite": {"name": "ماهواره", "cost": 5000, "power": 0, "category": "defense", "emoji": "🛰️", "level_req": 6},
    "space_station": {"name": "ایستگاه فضایی", "cost": 20000, "power": 2000, "category": "defense", "emoji": "🛰️", "level_req": 9},
    "force_field": {"name": "میدان نیرو", "cost": 15000, "power": 3000, "category": "defense", "emoji": "🛡️", "level_req": 8},
    "quantum_shield": {"name": "سپر کوانتومی", "cost": 30000, "power": 5000, "category": "defense", "emoji": "🛡️", "level_req": 10},
}

# Resource Types
RESOURCES = {
    "money": {"name": "پول", "emoji": "💰", "base_income": 100},
    "oil": {"name": "نفت", "emoji": "🛢️", "base_income": 50},
    "uranium": {"name": "اورانیوم", "emoji": "☢️", "base_income": 25},
    "social_credit": {"name": "اعتبار اجتماعی", "emoji": "⭐", "base_income": 10},
    "technology": {"name": "فناوری", "emoji": "🔬", "base_income": 5},
    "population": {"name": "جمعیت", "emoji": "👥", "base_income": 200},
    "steel": {"name": "فولاد", "emoji": "⚙️", "base_income": 75},
    "aluminum": {"name": "آلومینیوم", "emoji": "🔧", "base_income": 60},
    "titanium": {"name": "تیتانیوم", "emoji": "💎", "base_income": 40},
    "rare_earth": {"name": "فلزات نادر", "emoji": "💠", "base_income": 30},
}

# Capital Upgrades
CAPITAL_UPGRADES = {
    "government": {"name": "دولت", "levels": 10, "cost_multiplier": 1000, "benefits": ["income_bonus", "unit_discount"]},
    "military_academy": {"name": "آکادمی نظامی", "levels": 10, "cost_multiplier": 1500, "benefits": ["unit_power_bonus", "training_speed"]},
    "research_lab": {"name": "آزمایشگاه تحقیقاتی", "levels": 10, "cost_multiplier": 2000, "benefits": ["tech_bonus", "new_units"]},
    "infrastructure": {"name": "زیرساخت", "levels": 10, "cost_multiplier": 800, "benefits": ["resource_bonus", "defense_bonus"]},
    "intelligence": {"name": "سازمان اطلاعاتی", "levels": 10, "cost_multiplier": 1200, "benefits": ["spy_bonus", "intel_bonus"]},
    "economy": {"name": "اقتصاد", "levels": 10, "cost_multiplier": 1000, "benefits": ["money_bonus", "trade_bonus"]},
    "defense": {"name": "دفاع", "levels": 10, "cost_multiplier": 1800, "benefits": ["defense_bonus", "fortification"]},
    "diplomacy": {"name": "دیپلماسی", "levels": 10, "cost_multiplier": 900, "benefits": ["alliance_bonus", "trade_bonus"]},
    "space_program": {"name": "برنامه فضایی", "levels": 5, "cost_multiplier": 5000, "benefits": ["satellite_bonus", "space_units"]},
    "nuclear_program": {"name": "برنامه هسته‌ای", "levels": 5, "cost_multiplier": 10000, "benefits": ["nuclear_units", "deterrence"]},
}

# ==================== DATA MANAGEMENT ====================
def load_data():
    """بارگذاری داده‌ها از فایل"""
    global game_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
        else:
            game_data = {
                "users": {},
                "countries": {},
                "alliances": {},
                "battles": [],
                "logs": []
            }
    except Exception as e:
        print(f"خطا در بارگذاری داده‌ها: {e}")
        game_data = {
            "users": {},
            "countries": {},
            "alliances": {},
            "battles": [],
            "logs": []
        }

def save_data():
    """ذخیره داده‌ها در فایل"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطا در ذخیره داده‌ها: {e}")

def log_message(chat_id, user_id, message_type, content):
    """ثبت پیام در لاگ"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "type": message_type,
            "content": content
        }
        game_data["logs"].append(log_entry)
        
        # محدود کردن تعداد لاگ‌ها
        if len(game_data["logs"]) > 10000:
            game_data["logs"] = game_data["logs"][-5000:]  # نگه داشتن 5000 لاگ آخر
        
        # ذخیره در فایل لاگ
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {chat_id} | {user_id} | {message_type} | {content}\n")
        
        # ذخیره داده‌ها
        save_data()
        
    except Exception as e:
        print(f"خطا در ثبت لاگ: {e}")

def get_user_data(chat_id, user_id):
    """دریافت یا ایجاد داده کاربر"""
    user_key = f"{chat_id}:{user_id}"
    if user_key not in game_data["users"]:
        game_data["users"][user_key] = {
            "level": 1,
            "experience": 0,
            "resources": {resource: 1000 for resource in RESOURCES},
            "military": {},
            "capital": {upgrade: 0 for upgrade in CAPITAL_UPGRADES},
            "battles_won": 0,
            "battles_lost": 0,
            "territory_conquered": 0,
            "alliance": None,
            "last_active": datetime.now().isoformat(),
            "achievements": [],
            "research": {},
            "diplomacy": {},
            "spies": 0,
            "intelligence": 0
        }
    return game_data["users"][user_key]

def get_country_data(chat_id, user_id):
    """دریافت یا ایجاد داده کشور"""
    country_key = f"{chat_id}:{user_id}"
    if country_key not in game_data["countries"]:
        game_data["countries"][country_key] = {
            "name": f"کشور {user_id}",
            "level": 1,
            "population": 1000000,
            "territory": 1000,
            "defense_level": 1,
            "fortifications": 0,
            "conquered_by": None,
            "conquest_time": None,
            "rebellion_chance": 0.1
        }
    return game_data["countries"][country_key]

# ==================== HELPER FUNCTIONS ====================
def calculate_total_power(user_data):
    """محاسبه قدرت کل نظامی"""
    total_power = 0
    for unit_type, count in user_data["military"].items():
        if unit_type in MILITARY_UNITS and count > 0:
            unit_power = MILITARY_UNITS[unit_type]["power"]
            # اعمال بونوس آکادمی نظامی
            academy_level = user_data["capital"].get("military_academy", 0)
            power_bonus = 1 + (academy_level * 0.1)
            total_power += unit_power * count * power_bonus
    return int(total_power)

def calculate_country_level(user_data):
    """محاسبه سطح کشور بر اساس قدرت و منابع"""
    military_power = calculate_total_power(user_data)
    total_resources = sum(user_data["resources"].values())
    experience = user_data["experience"]
    
    # فرمول محاسبه سطح
    level = 1 + (military_power // 1000) + (total_resources // 10000) + (experience // 1000)
    return min(level, 50)  # حداکثر سطح 50

def can_afford_unit(user_data, unit_type, quantity=1):
    """بررسی امکان خرید واحد"""
    if unit_type not in MILITARY_UNITS:
        return False, "واحد نامعتبر"
    
    unit = MILITARY_UNITS[unit_type]
    user_level = user_data["level"]
    
    if user_level < unit["level_req"]:
        return False, f"نیاز به سطح {unit['level_req']}"
    
    # بررسی منابع مورد نیاز
    cost = unit["cost"] * quantity
    if user_data["resources"]["money"] < cost:
        return False, "پول کافی ندارید"
    
    return True, "موفق"

def can_attack(attacker_data, defender_data, attacker_country, defender_country):
    """بررسی امکان حمله"""
    attacker_level = attacker_country["level"]
    defender_level = defender_country["level"]
    
    # نمی‌توان به کشورهای خیلی قوی‌تر حمله کرد
    if defender_level > attacker_level * 2:
        return False, "کشور هدف خیلی قوی است"
    
    # بررسی اتحاد
    if (attacker_data["alliance"] and defender_data["alliance"] and 
        attacker_data["alliance"] == defender_data["alliance"]):
        return False, "نمی‌توان به متحد حمله کرد"
    
    return True, "موفق"

# ==================== BOT COMMANDS ====================
@bot.event
async def on_ready():
    """راه‌اندازی ربات"""
    print(f"🤖 {bot.user.username} آماده است!")
    load_data()
    log_message("system", "bot", "startup", "Bot started successfully")

@bot.event
async def on_message(message: Message):
    """مدیریت پیام‌ها"""
    try:
        if message.author.is_bot:
            return
        
        chat_id = message.chat.id
        user_id = message.author.user_id
        text = message.content or ""
        
        # ثبت لاگ
        log_message(chat_id, user_id, "message", text)
        
        # اعطای امتیاز برای فعالیت
        await handle_activity_points(message, chat_id, user_id)
        
        # پردازش دستورات
        if text.startswith("/"):
            await handle_command(message, text.lower(), chat_id, user_id)
        elif text in ["🏰 پایتخت", "⚔️ نیروی نظامی", "🛒 فروشگاه", "💰 وضعیت", "🏆 رتبه‌بندی", "🤝 اتحاد", "🕵️ جاسوسی", "🔬 تحقیقات", "🤝 دیپلماسی"]:
            await handle_menu_button(message, text, chat_id, user_id)
            
    except Exception as e:
        print(f"خطا در on_message: {e}")
        traceback.print_exc()

async def handle_activity_points(message, chat_id, user_id):
    """اعطای امتیاز برای فعالیت"""
    try:
        user_data = get_user_data(chat_id, user_id)
        current_time = datetime.now()
        last_active = datetime.fromisoformat(user_data["last_active"])
        
        # اعطای امتیاز هر 5 دقیقه
        if (current_time - last_active).seconds >= 300:
            # تولید منابع بر اساس سطح پایتخت
            government_level = user_data["capital"].get("government", 0)
            economy_level = user_data["capital"].get("economy", 0)
            
            # محاسبه درآمد
            money_income = 10 + (government_level * 5) + (economy_level * 3)
            oil_income = 5 + (government_level * 2)
            uranium_income = 1 + (government_level // 2)
            social_credit_income = 2 + (government_level // 3)
            technology_income = 1 + (user_data["capital"].get("research_lab", 0) * 2)
            
            # اعطای منابع
            user_data["resources"]["money"] += money_income
            user_data["resources"]["oil"] += oil_income
            user_data["resources"]["uranium"] += uranium_income
            user_data["resources"]["social_credit"] += social_credit_income
            user_data["resources"]["technology"] += technology_income
            user_data["experience"] += money_income // 2
            user_data["last_active"] = current_time.isoformat()
            save_data()
            
    except Exception as e:
        print(f"خطا در handle_activity_points: {e}")

async def handle_command(message, command, chat_id, user_id):
    """پردازش دستورات"""
    try:
        if command == "/start":
            await start_command(message)
        elif command == "/help":
            await help_command(message)
        elif command == "/status":
            await status_command(message, chat_id, user_id)
        elif command == "/military":
            await military_command(message, chat_id, user_id)
        elif command == "/shop":
            await shop_command(message, chat_id, user_id)
        elif command.startswith("/buy"):
            await buy_command(message, chat_id, user_id)
        elif command == "/attack":
            await attack_command(message, chat_id, user_id)
        elif command == "/capital":
            await capital_command(message, chat_id, user_id)
        elif command.startswith("/upgrade"):
            await upgrade_command(message, chat_id, user_id)
        elif command == "/alliance":
            await alliance_command(message, chat_id, user_id)
        elif command == "/leaderboard":
            await leaderboard_command(message, chat_id)
        elif command == "/clean":
            await clean_command(message, chat_id, user_id)
        elif command == "/spy":
            await spy_command(message, chat_id, user_id)
        elif command == "/research":
            await research_command(message, chat_id, user_id)
        elif command == "/diplomacy":
            await diplomacy_command(message, chat_id, user_id)
        elif command == "/collect":
            await collect_command(message, chat_id, user_id)
        elif command.startswith("/alliance"):
            await handle_alliance_command(message, chat_id, user_id)
        else:
            await message.reply("❌ دستور نامعتبر! از /help برای راهنمایی استفاده کنید.")
            
    except Exception as e:
        print(f"خطا در handle_command: {e}")
        traceback.print_exc()
        await message.reply("⚠️ خطایی رخ داد!")

# ==================== COMMAND IMPLEMENTATIONS ====================
async def start_command(message):
    """دستور شروع"""
    welcome_text = """
🎮 **ربات شبیه‌سازی جنگ پیشرفته** 🎮

خوش آمدید به دنیای جنگ و استراتژی!

**قابلیت‌های اصلی:**
🏰 **پایتخت**: سیستم اپگرید پیشرفته
⚔️ **120+ واحد نظامی**: از سرباز تا سلاح‌های هسته‌ای
💰 **منابع متنوع**: پول، نفت، اورانیوم، فناوری و...
🌍 **فتح کشورها**: حمله و فتح کشورهای دیگر
🤝 **اتحاد و دیپلماسی**: تشکیل اتحاد و مذاکره
🔬 **تحقیقات**: توسعه فناوری‌های جدید
🕵️ **جاسوسی**: جمع‌آوری اطلاعات دشمن

**دستورات اصلی:**
/status - وضعیت کشور شما
/military - نیروی نظامی
/shop - فروشگاه
/capital - پایتخت
/attack - حمله
/alliance - اتحادها
/leaderboard - رتبه‌بندی

برای شروع از دکمه‌های زیر استفاده کنید!
    """
    
    # ایجاد کیبورد منو
    keyboard = MenuKeyboardMarkup()
    keyboard.add(MenuKeyboardButton("💰 وضعیت"))
    keyboard.add(MenuKeyboardButton("⚔️ نیروی نظامی"))
    keyboard.add(MenuKeyboardButton("🛒 فروشگاه"))
    keyboard.add(MenuKeyboardButton("🏰 پایتخت"))
    keyboard.add(MenuKeyboardButton("🏆 رتبه‌بندی"))
    keyboard.add(MenuKeyboardButton("🤝 اتحاد"))
    keyboard.add(MenuKeyboardButton("🕵️ جاسوسی"))
    keyboard.add(MenuKeyboardButton("🔬 تحقیقات"))
    keyboard.add(MenuKeyboardButton("🤝 دیپلماسی"))
    
    await message.reply(welcome_text, components=keyboard)

async def help_command(message):
    """دستور راهنما"""
    help_text = """
📖 **راهنمای کامل ربات جنگ** 📖

**دستورات اصلی:**
/status - وضعیت کامل کشور
/military - نمایش نیروی نظامی
/shop - فروشگاه واحدها
/capital - مدیریت پایتخت
/attack - حمله به کشور دیگر
/alliance - مدیریت اتحادها
/leaderboard - جدول رتبه‌بندی
/spy - عملیات جاسوسی
/research - تحقیقات
/diplomacy - دیپلماسی
/collect - جمع‌آوری منابع
/clean - پاکسازی پیام‌ها

**دستورات اتحاد:**
/alliance create [نام] - ایجاد اتحاد
/alliance join [نام] - پیوستن به اتحاد
/alliance leave - ترک اتحاد
/alliance list - لیست اتحادها
/alliance info [نام] - اطلاعات اتحاد
/alliance invite [ریپلای] - دعوت عضو
/alliance kick [ریپلای] - اخراج عضو

**منابع:**
💰 پول - برای خرید واحدها
🛢️ نفت - برای سوخت
☢️ اورانیوم - برای سلاح‌های هسته‌ای
⭐ اعتبار اجتماعی - برای دیپلماسی
🔬 فناوری - برای تحقیقات
👥 جمعیت - برای نیروی کار
⚙️ فولاد - برای ساخت تجهیزات
🔧 آلومینیوم - برای هواپیماها
💎 تیتانیوم - برای فضاپیماها
💠 فلزات نادر - برای فناوری پیشرفته

**نکات مهم:**
• هر 5 دقیقه منابع تولید می‌شود
• از /collect برای جمع‌آوری استفاده کنید
• سطح کشور بر اساس قدرت و منابع محاسبه می‌شود
• نمی‌توان به کشورهای خیلی قوی‌تر حمله کرد
• اتحادها از حمله متقابل جلوگیری می‌کنند
• 120+ واحد نظامی مختلف در دسترس است
    """
    
    # ایجاد کیبورد منو
    keyboard = MenuKeyboardMarkup()
    keyboard.add(MenuKeyboardButton("💰 وضعیت"))
    keyboard.add(MenuKeyboardButton("⚔️ نیروی نظامی"))
    keyboard.add(MenuKeyboardButton("🛒 فروشگاه"))
    keyboard.add(MenuKeyboardButton("🏰 پایتخت"))
    keyboard.add(MenuKeyboardButton("🏆 رتبه‌بندی"))
    keyboard.add(MenuKeyboardButton("🤝 اتحاد"))
    keyboard.add(MenuKeyboardButton("🕵️ جاسوسی"))
    keyboard.add(MenuKeyboardButton("🔬 تحقیقات"))
    keyboard.add(MenuKeyboardButton("🤝 دیپلماسی"))
    
    await message.reply(help_text, components=keyboard)

async def status_command(message, chat_id, user_id):
    """دستور وضعیت"""
    try:
        user_data = get_user_data(chat_id, user_id)
        country_data = get_country_data(chat_id, user_id)
        
        # محاسبه آمار
        total_power = calculate_total_power(user_data)
        country_level = calculate_country_level(user_data)
        
        # به‌روزرسانی سطح
        if country_level > user_data["level"]:
            user_data["level"] = country_level
            save_data()
        
        status_text = f"""
🏰 **وضعیت کشور {country_data['name']}** 🏰

**📊 آمار کلی:**
🎖️ سطح: {user_data['level']}
💪 قدرت نظامی: {total_power:,}
👥 جمعیت: {country_data['population']:,}
🌍 قلمرو: {country_data['territory']:,} کیلومتر مربع
🏆 پیروزی: {user_data['battles_won']} | 💀 شکست: {user_data['battles_lost']}

**💰 منابع:**
"""
        
        for resource, amount in user_data["resources"].items():
            emoji = RESOURCES[resource]["emoji"]
            name = RESOURCES[resource]["name"]
            status_text += f"{emoji} {name}: {amount:,}\n"
        
        status_text += f"""
**🏛️ پایتخت:**
"""
        
        for upgrade, level in user_data["capital"].items():
            if level > 0:
                name = CAPITAL_UPGRADES[upgrade]["name"]
                status_text += f"• {name}: سطح {level}\n"
        
        if user_data["alliance"]:
            status_text += f"\n🤝 اتحاد: {user_data['alliance']}"
        
        await message.reply(status_text)
        
    except Exception as e:
        print(f"خطا در status_command: {e}")
        await message.reply("⚠️ خطا در نمایش وضعیت!")

async def military_command(message, chat_id, user_id):
    """دستور نیروی نظامی"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        military_text = "⚔️ **نیروی نظامی شما** ⚔️\n\n"
        
        # دسته‌بندی واحدها
        categories = {}
        for unit_type, count in user_data["military"].items():
            if count > 0 and unit_type in MILITARY_UNITS:
                unit = MILITARY_UNITS[unit_type]
                category = unit["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append((unit_type, count, unit))
        
        # نمایش هر دسته
        category_names = {
            "infantry": "پیاده نظام",
            "light_vehicle": "خودروهای سبک",
            "tank": "تانک‌ها",
            "artillery": "توپخانه",
            "anti_air": "ضدهوایی",
            "fighter": "جنگنده‌ها",
            "bomber": "بمب‌افکن‌ها",
            "helicopter": "هلیکوپترها",
            "drone": "پهپادها",
            "naval": "نیروی دریایی",
            "missile": "موشک‌ها",
            "special": "سلاح‌های ویژه",
            "defense": "سیستم‌های دفاعی"
        }
        
        for category, units in categories.items():
            category_name = category_names.get(category, category)
            military_text += f"**{category_name}:**\n"
            for unit_type, count, unit in units:
                power = unit["power"] * count
                military_text += f"• {unit['emoji']} {unit['name']}: {count} (قدرت: {power})\n"
            military_text += "\n"
        
        total_power = calculate_total_power(user_data)
        military_text += f"**💪 قدرت کل: {total_power:,}**"
        
        await message.reply(military_text)
        
    except Exception as e:
        print(f"خطا در military_command: {e}")
        await message.reply("⚠️ خطا در نمایش نیروی نظامی!")

async def shop_command(message, chat_id, user_id):
    """دستور فروشگاه"""
    try:
        user_data = get_user_data(chat_id, user_id)
        user_level = user_data["level"]
        
        shop_text = "🛒 **فروشگاه واحدهای نظامی** 🛒\n\n"
        shop_text += f"سطح شما: {user_level}\n"
        shop_text += f"💰 پول: {user_data['resources']['money']:,}\n\n"
        
        # دسته‌بندی واحدها بر اساس دسترسی
        available_units = []
        locked_units = []
        
        for unit_type, unit in MILITARY_UNITS.items():
            if user_level >= unit["level_req"]:
                available_units.append((unit_type, unit))
            else:
                locked_units.append((unit_type, unit))
        
        # نمایش واحدهای در دسترس
        shop_text += "**✅ واحدهای در دسترس:**\n"
        for unit_type, unit in available_units[:20]:  # نمایش 20 واحد اول
            shop_text += f"• {unit['emoji']} {unit['name']} - {unit['cost']:,} 💰 (سطح {unit['level_req']})\n"
        
        if len(available_units) > 20:
            shop_text += f"... و {len(available_units) - 20} واحد دیگر\n"
        
        # نمایش واحدهای قفل شده
        if locked_units:
            shop_text += f"\n**🔒 واحدهای قفل شده:**\n"
            for unit_type, unit in locked_units[:10]:
                shop_text += f"• {unit['emoji']} {unit['name']} - سطح {unit['level_req']} مورد نیاز\n"
        
        shop_text += "\n**برای خرید از دستور زیر استفاده کنید:**\n"
        shop_text += "`/buy [نوع_واحد] [تعداد]`\n"
        shop_text += "مثال: `/buy soldier 10`"
        
        await message.reply(shop_text)
        
    except Exception as e:
        print(f"خطا در shop_command: {e}")
        await message.reply("⚠️ خطا در نمایش فروشگاه!")

async def buy_command(message, chat_id, user_id):
    """دستور خرید"""
    try:
        parts = message.content.split()
        if len(parts) < 2:
            await message.reply("❌ فرمت صحیح: `/buy [نوع_واحد] [تعداد]`")
            return
        
        unit_type = parts[1].lower()
        quantity = int(parts[2]) if len(parts) > 2 else 1
        
        if quantity <= 0:
            await message.reply("❌ تعداد باید بیشتر از صفر باشد!")
            return
        
        user_data = get_user_data(chat_id, user_id)
        
        # بررسی امکان خرید
        can_buy, reason = can_afford_unit(user_data, unit_type, quantity)
        if not can_buy:
            await message.reply(f"❌ {reason}")
            return
        
        # خرید واحد
        unit = MILITARY_UNITS[unit_type]
        total_cost = unit["cost"] * quantity
        
        user_data["resources"]["money"] -= total_cost
        user_data["military"][unit_type] = user_data["military"].get(unit_type, 0) + quantity
        user_data["experience"] += total_cost // 10
        
        save_data()
        
        success_text = f"""
✅ **خرید موفق!**

{unit['emoji']} **{unit['name']}** x{quantity}
💰 هزینه: {total_cost:,}
💪 قدرت اضافه شده: {unit['power'] * quantity:,}

💰 پول باقیمانده: {user_data['resources']['money']:,}
        """
        
        await message.reply(success_text)
        
    except ValueError:
        await message.reply("❌ تعداد باید یک عدد باشد!")
    except Exception as e:
        print(f"خطا در buy_command: {e}")
        await message.reply("⚠️ خطا در خرید!")

async def attack_command(message, chat_id, user_id):
    """دستور حمله"""
    try:
        if not message.reply_to_message:
            await message.reply("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید!")
            return
        
        target_user = message.reply_to_message.author
        if target_user.user_id == user_id:
            await message.reply("❌ نمی‌توانید به خودتان حمله کنید!")
            return
        
        attacker_data = get_user_data(chat_id, user_id)
        defender_data = get_user_data(chat_id, target_user.user_id)
        attacker_country = get_country_data(chat_id, user_id)
        defender_country = get_country_data(chat_id, target_user.user_id)
        
        # بررسی امکان حمله
        can_attack_result, reason = can_attack(attacker_data, defender_data, attacker_country, defender_country)
        if not can_attack_result:
            await message.reply(f"❌ {reason}")
            return
        
        # محاسبه قدرت
        attacker_power = calculate_total_power(attacker_data)
        defender_power = calculate_total_power(defender_data)
        
        if attacker_power < 100:
            await message.reply("❌ برای حمله حداقل 100 قدرت نظامی نیاز دارید!")
            return
        
        # محاسبه نتیجه نبرد
        attack_strength = attacker_power * random.uniform(0.8, 1.2)
        defense_strength = defender_power * random.uniform(0.8, 1.2)
        
        if attack_strength > defense_strength:
            # حمله کننده برنده شد
            damage_ratio = min(0.3, (attack_strength - defense_strength) / attack_strength * 0.5)
            stolen_money = int(defender_data["resources"]["money"] * damage_ratio)
            stolen_oil = int(defender_data["resources"]["oil"] * damage_ratio)
            
            # انتقال منابع
            attacker_data["resources"]["money"] += stolen_money
            attacker_data["resources"]["oil"] += stolen_oil
            defender_data["resources"]["money"] = max(0, defender_data["resources"]["money"] - stolen_money)
            defender_data["resources"]["oil"] = max(0, defender_data["resources"]["oil"] - stolen_oil)
            
            # ثبت آمار
            attacker_data["battles_won"] += 1
            defender_data["battles_lost"] += 1
            attacker_data["experience"] += 100
            defender_data["experience"] += 50
            
            # بررسی فتح کشور
            conquest_chance = min(0.1, (attack_strength - defense_strength) / attack_strength * 0.2)
            if random.random() < conquest_chance:
                defender_country["conquered_by"] = user_id
                defender_country["conquest_time"] = datetime.now().isoformat()
                attacker_data["territory_conquered"] += defender_country["territory"]
                conquest_text = f"\n🏰 **کشور فتح شد!** قلمرو: +{defender_country['territory']:,}"
            else:
                conquest_text = ""
            
            result_text = f"""
⚔️ **حمله موفق!** ⚔️

{message.author.first_name} به {target_user.first_name} حمله کرد و پیروز شد!

💰 غنیمت: {stolen_money:,} پول + {stolen_oil:,} نفت
💪 قدرت حمله: {int(attack_strength):,}
🛡️ قدرت دفاع: {int(defense_strength):,}
{conquest_text}
            """
        else:
            # مدافع برنده شد
            damage_ratio = min(0.2, (defense_strength - attack_strength) / defense_strength * 0.3)
            lost_money = int(attacker_data["resources"]["money"] * damage_ratio)
            
            # جریمه حمله کننده
            attacker_data["resources"]["money"] = max(0, attacker_data["resources"]["money"] - lost_money)
            
            # ثبت آمار
            attacker_data["battles_lost"] += 1
            defender_data["battles_won"] += 1
            attacker_data["experience"] += 25
            defender_data["experience"] += 75
            
            result_text = f"""
🛡️ **دفاع موفق!** 🛡️

{message.author.first_name} به {target_user.first_name} حمله کرد اما شکست خورد!

💸 جریمه: {lost_money:,} پول
💪 قدرت حمله: {int(attack_strength):,}
🛡️ قدرت دفاع: {int(defense_strength):,}
            """
        
        save_data()
        await message.reply(result_text)
        
    except Exception as e:
        print(f"خطا در attack_command: {e}")
        await message.reply("⚠️ خطا در انجام حمله!")

async def capital_command(message, chat_id, user_id):
    """دستور پایتخت"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        capital_text = "🏰 **پایتخت شما** 🏰\n\n"
        
        for upgrade, level in user_data["capital"].items():
            upgrade_info = CAPITAL_UPGRADES[upgrade]
            cost = upgrade_info["cost_multiplier"] * (level + 1)
            
            capital_text += f"**{upgrade_info['name']}** (سطح {level})\n"
            capital_text += f"💰 هزینه اپگرید: {cost:,}\n"
            capital_text += f"📈 مزایا: {', '.join(upgrade_info['benefits'])}\n\n"
        
        capital_text += "**برای اپگرید از دستور زیر استفاده کنید:**\n"
        capital_text += "`/upgrade [نام_اپگرید]`\n"
        capital_text += "مثال: `/upgrade government`"
        
        await message.reply(capital_text)
        
    except Exception as e:
        print(f"خطا در capital_command: {e}")
        await message.reply("⚠️ خطا در نمایش پایتخت!")

async def upgrade_command(message, chat_id, user_id):
    """دستور اپگرید"""
    try:
        parts = message.content.split()
        if len(parts) < 2:
            await message.reply("❌ فرمت صحیح: `/upgrade [نام_اپگرید]`")
            return
        
        upgrade_name = parts[1].lower()
        if upgrade_name not in CAPITAL_UPGRADES:
            await message.reply("❌ اپگرید نامعتبر!")
            return
        
        user_data = get_user_data(chat_id, user_id)
        current_level = user_data["capital"][upgrade_name]
        upgrade_info = CAPITAL_UPGRADES[upgrade_name]
        
        # بررسی حداکثر سطح
        max_level = upgrade_info["levels"]
        if current_level >= max_level:
            await message.reply(f"❌ {upgrade_info['name']} در حداکثر سطح است!")
            return
        
        # محاسبه هزینه
        cost = upgrade_info["cost_multiplier"] * (current_level + 1)
        
        if user_data["resources"]["money"] < cost:
            await message.reply(f"❌ پول کافی ندارید! نیاز: {cost:,}")
            return
        
        # انجام اپگرید
        user_data["resources"]["money"] -= cost
        user_data["capital"][upgrade_name] += 1
        user_data["experience"] += cost // 100
        
        save_data()
        
        success_text = f"""
✅ **اپگرید موفق!**

🏛️ {upgrade_info['name']} به سطح {current_level + 1} ارتقا یافت!
💰 هزینه: {cost:,}
📈 مزایا: {', '.join(upgrade_info['benefits'])}

💰 پول باقیمانده: {user_data['resources']['money']:,}
        """
        
        await message.reply(success_text)
        
    except Exception as e:
        print(f"خطا در upgrade_command: {e}")
        await message.reply("⚠️ خطا در اپگرید!")

async def alliance_command(message, chat_id, user_id):
    """دستور اتحاد"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        if user_data["alliance"]:
            # نمایش اطلاعات اتحاد فعلی
            alliance_name = user_data["alliance"]
            alliance_data = game_data["alliances"].get(alliance_name, {})
            
            alliance_text = f"""
🤝 **اتحاد شما: {alliance_name}** 🤝

**اطلاعات اتحاد:**
👑 رهبر: {alliance_data.get('leader', 'نامشخص')}
👥 اعضا: {len(alliance_data.get('members', []))} نفر
📅 تاریخ ایجاد: {alliance_data.get('created_at', 'نامشخص')}
💪 قدرت کل: {alliance_data.get('total_power', 0):,}

**اعضا:**
"""
            
            for member_id in alliance_data.get('members', []):
                try:
                    member = await bot.get_chat_member(chat_id, int(member_id))
                    member_name = member.user.first_name
                    if member_id == alliance_data.get('leader'):
                        alliance_text += f"👑 {member_name} (رهبر)\n"
                    else:
                        alliance_text += f"• {member_name}\n"
                except:
                    alliance_text += f"• User {member_id}\n"
            
            alliance_text += "\n**دستورات:**
/alliance leave - ترک اتحاد
/alliance kick [ریپلای] - اخراج عضو
/alliance invite [ریپلای] - دعوت عضو جدید"
            
        else:
            # نمایش لیست اتحادهای موجود
            alliance_text = """
🤝 **سیستم اتحاد** 🤝

**اتحادهای موجود:**
"""
            
            for alliance_name, alliance_data in game_data["alliances"].items():
                member_count = len(alliance_data.get('members', []))
                total_power = alliance_data.get('total_power', 0)
                alliance_text += f"• **{alliance_name}** ({member_count} عضو, قدرت: {total_power:,})\n"
            
            alliance_text += """
**دستورات:**
/alliance create [نام] - ایجاد اتحاد جدید
/alliance join [نام] - پیوستن به اتحاد
/alliance info [نام] - اطلاعات اتحاد

**مزایای اتحاد:**
• محافظت از حمله متقابل
• بونوس قدرت در نبردهای مشترک
• اشتراک‌گذاری منابع
• دسترسی به فناوری‌های پیشرفته
            """
        
        await message.reply(alliance_text)
        
    except Exception as e:
        print(f"خطا در alliance_command: {e}")
        await message.reply("⚠️ خطا در نمایش اتحادها!")

async def leaderboard_command(message, chat_id):
    """دستور رتبه‌بندی"""
    try:
        # جمع‌آوری آمار کاربران
        leaderboard = []
        for user_key, user_data in game_data["users"].items():
            if user_key.startswith(f"{chat_id}:"):
                user_id = user_key.split(":")[1]
                power = calculate_total_power(user_data)
                leaderboard.append({
                    "user_id": user_id,
                    "power": power,
                    "level": user_data["level"],
                    "battles_won": user_data["battles_won"]
                })
        
        # مرتب‌سازی بر اساس قدرت
        leaderboard.sort(key=lambda x: x["power"], reverse=True)
        
        leaderboard_text = "🏆 **جدول رتبه‌بندی** 🏆\n\n"
        
        for i, player in enumerate(leaderboard[:10], 1):
            try:
                user = await bot.get_chat_member(chat_id, int(player["user_id"]))
                username = user.user.first_name
            except:
                username = f"User {player['user_id']}"
            
            leaderboard_text += f"{i}. **{username}**\n"
            leaderboard_text += f"   💪 قدرت: {player['power']:,} | 🎖️ سطح: {player['level']} | 🏆 برد: {player['battles_won']}\n\n"
        
        await message.reply(leaderboard_text)
        
    except Exception as e:
        print(f"خطا در leaderboard_command: {e}")
        await message.reply("⚠️ خطا در نمایش رتبه‌بندی!")

async def clean_command(message, chat_id, user_id):
    """دستور پاکسازی"""
    try:
        # بررسی دسترسی ادمین
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status not in ["administrator", "creator"]:
                await message.reply("❌ فقط ادمین‌ها می‌توانند از این دستور استفاده کنند!")
                return
        except:
            await message.reply("❌ خطا در بررسی دسترسی!")
            return
        
        # حذف پیام‌های ربات
        deleted_count = 0
        try:
            # حذف پیام فعلی
            await message.delete()
            deleted_count = 1
            
            # تلاش برای حذف پیام‌های قبلی ربات
            # این بخش نیاز به API خاص دارد
            # در اینجا فقط پیام فعلی را حذف می‌کنیم
            
        except Exception as e:
            print(f"خطا در حذف پیام: {e}")
        
        # ثبت در لاگ
        log_message(chat_id, user_id, "clean", f"Cleaned {deleted_count} messages")
        
        # ارسال پیام تأیید (که خودش هم حذف خواهد شد)
        confirm_msg = await message.reply(f"✅ {deleted_count} پیام حذف شد!")
        
        # حذف پیام تأیید پس از 3 ثانیه
        await asyncio.sleep(3)
        try:
            await confirm_msg.delete()
        except:
            pass
        
    except Exception as e:
        print(f"خطا در clean_command: {e}")
        await message.reply("⚠️ خطا در پاکسازی!")

async def spy_command(message, chat_id, user_id):
    """دستور جاسوسی"""
    try:
        if not message.reply_to_message:
            await message.reply("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید!")
            return
        
        target_user = message.reply_to_message.author
        if target_user.user_id == user_id:
            await message.reply("❌ نمی‌توانید خودتان را جاسوسی کنید!")
            return
        
        user_data = get_user_data(chat_id, user_id)
        target_data = get_user_data(chat_id, target_user.user_id)
        
        # بررسی سطح جاسوسی
        spy_level = user_data["capital"].get("intelligence", 0)
        if spy_level < 1:
            await message.reply("❌ برای جاسوسی نیاز به سطح 1 سازمان اطلاعاتی دارید!")
            return
        
        # محاسبه موفقیت جاسوسی
        success_chance = min(0.8, 0.3 + (spy_level * 0.1))
        if random.random() < success_chance:
            # جاسوسی موفق
            target_power = calculate_total_power(target_data)
            target_level = target_data["level"]
            
            spy_text = f"""
🕵️ **گزارش جاسوسی موفق!**

**هدف:** {target_user.first_name}
💪 قدرت نظامی: {target_power:,}
🎖️ سطح: {target_level}
💰 پول: {target_data['resources']['money']:,}
🛢️ نفت: {target_data['resources']['oil']:,}
☢️ اورانیوم: {target_data['resources']['uranium']:,}

**نیروی نظامی:**
"""
            
            # نمایش 5 واحد اصلی
            military_items = list(target_data["military"].items())
            military_items.sort(key=lambda x: MILITARY_UNITS.get(x[0], {}).get("power", 0) * x[1], reverse=True)
            
            for unit_type, count in military_items[:5]:
                if unit_type in MILITARY_UNITS and count > 0:
                    unit = MILITARY_UNITS[unit_type]
                    spy_text += f"• {unit['emoji']} {unit['name']}: {count}\n"
            
            user_data["intelligence"] += 10
            save_data()
            
        else:
            # جاسوسی ناموفق
            spy_text = f"""
🕵️ **جاسوسی ناموفق!**

نمی‌توان اطلاعاتی از {target_user.first_name} جمع‌آوری کرد.
احتمالاً متوجه شده‌اند!
            """
            
            user_data["intelligence"] += 1
            save_data()
        
        await message.reply(spy_text)
        
    except Exception as e:
        print(f"خطا در spy_command: {e}")
        await message.reply("⚠️ خطا در جاسوسی!")

async def research_command(message, chat_id, user_id):
    """دستور تحقیقات"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        research_text = """
🔬 **مرکز تحقیقات** 🔬

**تحقیقات در دسترس:**
• فناوری نظامی - بهبود قدرت واحدها
• فناوری دفاعی - افزایش مقاومت
• فناوری اقتصادی - بهبود درآمد
• فناوری اطلاعاتی - بهبود جاسوسی
• فناوری فضایی - دسترسی به واحدهای فضایی

**برای شروع تحقیق از دستور زیر استفاده کنید:**
`/research start [نوع_تحقیق]`
        """
        
        await message.reply(research_text)
        
    except Exception as e:
        print(f"خطا در research_command: {e}")
        await message.reply("⚠️ خطا در نمایش تحقیقات!")

async def diplomacy_command(message, chat_id, user_id):
    """دستور دیپلماسی"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        diplomacy_text = """
🤝 **وزارت امور خارجه** 🤝

**گزینه‌های دیپلماسی:**
• مذاکره تجاری - افزایش درآمد
• پیمان عدم تجاوز - محافظت متقابل
• اتحاد نظامی - همکاری در نبرد
• تحریم اقتصادی - کاهش درآمد دشمن
• مذاکره صلح - پایان جنگ

**برای شروع مذاکره از دستور زیر استفاده کنید:**
`/diplomacy negotiate [کاربر] [نوع]`
        """
        
        await message.reply(diplomacy_text)
        
    except Exception as e:
        print(f"خطا در diplomacy_command: {e}")
        await message.reply("⚠️ خطا در نمایش دیپلماسی!")

async def collect_command(message, chat_id, user_id):
    """دستور جمع‌آوری منابع"""
    try:
        user_data = get_user_data(chat_id, user_id)
        current_time = datetime.now()
        last_active = datetime.fromisoformat(user_data["last_active"])
        
        # محاسبه منابع قابل جمع‌آوری
        time_diff = (current_time - last_active).total_seconds() / 60  # دقیقه
        
        if time_diff < 5:
            await message.reply("⏳ هنوز منابع جدید تولید نشده! 5 دقیقه صبر کنید.")
            return
        
        # محاسبه منابع بر اساس زمان
        cycles = int(time_diff // 5)
        
        # محاسبه درآمد
        government_level = user_data["capital"].get("government", 0)
        economy_level = user_data["capital"].get("economy", 0)
        infrastructure_level = user_data["capital"].get("infrastructure", 0)
        
        money_income = (10 + (government_level * 5) + (economy_level * 3)) * cycles
        oil_income = (5 + (government_level * 2) + (infrastructure_level * 1)) * cycles
        uranium_income = (1 + (government_level // 2)) * cycles
        social_credit_income = (2 + (government_level // 3)) * cycles
        technology_income = (1 + (user_data["capital"].get("research_lab", 0) * 2)) * cycles
        steel_income = (3 + (infrastructure_level * 2)) * cycles
        aluminum_income = (2 + (infrastructure_level * 1)) * cycles
        titanium_income = (1 + (infrastructure_level // 2)) * cycles
        rare_earth_income = (1 + (infrastructure_level // 3)) * cycles
        population_income = (20 + (government_level * 10)) * cycles
        
        # اعطای منابع
        user_data["resources"]["money"] += money_income
        user_data["resources"]["oil"] += oil_income
        user_data["resources"]["uranium"] += uranium_income
        user_data["resources"]["social_credit"] += social_credit_income
        user_data["resources"]["technology"] += technology_income
        user_data["resources"]["steel"] += steel_income
        user_data["resources"]["aluminum"] += aluminum_income
        user_data["resources"]["titanium"] += titanium_income
        user_data["resources"]["rare_earth"] += rare_earth_income
        user_data["resources"]["population"] += population_income
        user_data["experience"] += money_income // 10
        user_data["last_active"] = current_time.isoformat()
        
        save_data()
        
        collect_text = f"""
💰 **جمع‌آوری منابع موفق!**

**منابع جمع‌آوری شده:**
💰 پول: +{money_income:,}
🛢️ نفت: +{oil_income:,}
☢️ اورانیوم: +{uranium_income:,}
⭐ اعتبار اجتماعی: +{social_credit_income:,}
🔬 فناوری: +{technology_income:,}
⚙️ فولاد: +{steel_income:,}
🔧 آلومینیوم: +{aluminum_income:,}
💎 تیتانیوم: +{titanium_income:,}
💠 فلزات نادر: +{rare_earth_income:,}
👥 جمعیت: +{population_income:,}

**مجموع چرخه‌ها:** {cycles}
**تجربه کسب شده:** +{money_income // 10:,}
        """
        
        await message.reply(collect_text)
        
    except Exception as e:
        print(f"خطا در collect_command: {e}")
        await message.reply("⚠️ خطا در جمع‌آوری منابع!")

async def handle_alliance_command(message, chat_id, user_id):
    """مدیریت دستورات اتحاد"""
    try:
        parts = message.content.split()
        if len(parts) < 2:
            await alliance_command(message, chat_id, user_id)
            return
        
        subcommand = parts[1].lower()
        
        if subcommand == "create" and len(parts) >= 3:
            await alliance_create(message, chat_id, user_id, " ".join(parts[2:]))
        elif subcommand == "join" and len(parts) >= 3:
            await alliance_join(message, chat_id, user_id, " ".join(parts[2:]))
        elif subcommand == "leave":
            await alliance_leave(message, chat_id, user_id)
        elif subcommand == "info" and len(parts) >= 3:
            await alliance_info(message, chat_id, " ".join(parts[2:]))
        elif subcommand == "list":
            await alliance_list(message, chat_id)
        elif subcommand == "invite":
            await alliance_invite(message, chat_id, user_id)
        elif subcommand == "kick":
            await alliance_kick(message, chat_id, user_id)
        else:
            await message.reply("❌ دستور اتحاد نامعتبر!")
            
    except Exception as e:
        print(f"خطا در handle_alliance_command: {e}")
        await message.reply("⚠️ خطا در پردازش دستور اتحاد!")

async def alliance_create(message, chat_id, user_id, alliance_name):
    """ایجاد اتحاد جدید"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        if user_data["alliance"]:
            await message.reply("❌ شما قبلاً در یک اتحاد عضو هستید!")
            return
        
        if alliance_name in game_data["alliances"]:
            await message.reply("❌ اتحادی با این نام از قبل وجود دارد!")
            return
        
        # ایجاد اتحاد
        game_data["alliances"][alliance_name] = {
            "leader": user_id,
            "members": [user_id],
            "created_at": datetime.now().isoformat(),
            "total_power": calculate_total_power(user_data)
        }
        
        user_data["alliance"] = alliance_name
        save_data()
        
        await message.reply(f"✅ اتحاد '{alliance_name}' با موفقیت ایجاد شد!")
        
    except Exception as e:
        print(f"خطا در alliance_create: {e}")
        await message.reply("⚠️ خطا در ایجاد اتحاد!")

async def alliance_join(message, chat_id, user_id, alliance_name):
    """پیوستن به اتحاد"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        if user_data["alliance"]:
            await message.reply("❌ شما قبلاً در یک اتحاد عضو هستید!")
            return
        
        if alliance_name not in game_data["alliances"]:
            await message.reply("❌ اتحادی با این نام وجود ندارد!")
            return
        
        # پیوستن به اتحاد
        game_data["alliances"][alliance_name]["members"].append(user_id)
        game_data["alliances"][alliance_name]["total_power"] += calculate_total_power(user_data)
        
        user_data["alliance"] = alliance_name
        save_data()
        
        await message.reply(f"✅ شما با موفقیت به اتحاد '{alliance_name}' پیوستید!")
        
    except Exception as e:
        print(f"خطا در alliance_join: {e}")
        await message.reply("⚠️ خطا در پیوستن به اتحاد!")

async def alliance_leave(message, chat_id, user_id):
    """ترک اتحاد"""
    try:
        user_data = get_user_data(chat_id, user_id)
        
        if not user_data["alliance"]:
            await message.reply("❌ شما در هیچ اتحادی عضو نیستید!")
            return
        
        alliance_name = user_data["alliance"]
        alliance_data = game_data["alliances"][alliance_name]
        
        # حذف از اتحاد
        if user_id in alliance_data["members"]:
            alliance_data["members"].remove(user_id)
            alliance_data["total_power"] -= calculate_total_power(user_data)
        
        # اگر رهبر بود، رهبر جدید انتخاب کن
        if alliance_data["leader"] == user_id and alliance_data["members"]:
            alliance_data["leader"] = alliance_data["members"][0]
        elif not alliance_data["members"]:
            # اگر اتحاد خالی شد، حذف کن
            del game_data["alliances"][alliance_name]
        
        user_data["alliance"] = None
        save_data()
        
        await message.reply(f"✅ شما با موفقیت از اتحاد '{alliance_name}' خارج شدید!")
        
    except Exception as e:
        print(f"خطا در alliance_leave: {e}")
        await message.reply("⚠️ خطا در ترک اتحاد!")

async def alliance_info(message, chat_id, alliance_name):
    """اطلاعات اتحاد"""
    try:
        if alliance_name not in game_data["alliances"]:
            await message.reply("❌ اتحادی با این نام وجود ندارد!")
            return
        
        alliance_data = game_data["alliances"][alliance_name]
        
        info_text = f"""
🤝 **اطلاعات اتحاد: {alliance_name}** 🤝

👑 رهبر: {alliance_data.get('leader', 'نامشخص')}
👥 اعضا: {len(alliance_data.get('members', []))} نفر
💪 قدرت کل: {alliance_data.get('total_power', 0):,}
📅 تاریخ ایجاد: {alliance_data.get('created_at', 'نامشخص')}

**اعضا:**
"""
        
        for member_id in alliance_data.get('members', []):
            try:
                member = await bot.get_chat_member(chat_id, int(member_id))
                member_name = member.user.first_name
                if member_id == alliance_data.get('leader'):
                    info_text += f"👑 {member_name} (رهبر)\n"
                else:
                    info_text += f"• {member_name}\n"
            except:
                info_text += f"• User {member_id}\n"
        
        await message.reply(info_text)
        
    except Exception as e:
        print(f"خطا در alliance_info: {e}")
        await message.reply("⚠️ خطا در دریافت اطلاعات اتحاد!")

async def alliance_list(message, chat_id):
    """لیست اتحادها"""
    try:
        if not game_data["alliances"]:
            await message.reply("❌ هیچ اتحادی وجود ندارد!")
            return
        
        list_text = "🤝 **لیست اتحادها** 🤝\n\n"
        
        for alliance_name, alliance_data in game_data["alliances"].items():
            member_count = len(alliance_data.get('members', []))
            total_power = alliance_data.get('total_power', 0)
            list_text += f"• **{alliance_name}**\n"
            list_text += f"  👥 اعضا: {member_count} | 💪 قدرت: {total_power:,}\n\n"
        
        await message.reply(list_text)
        
    except Exception as e:
        print(f"خطا در alliance_list: {e}")
        await message.reply("⚠️ خطا در دریافت لیست اتحادها!")

async def alliance_invite(message, chat_id, user_id):
    """دعوت به اتحاد"""
    try:
        if not message.reply_to_message:
            await message.reply("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید!")
            return
        
        target_user = message.reply_to_message.author
        target_user_id = target_user.user_id
        
        user_data = get_user_data(chat_id, user_id)
        target_data = get_user_data(chat_id, target_user_id)
        
        if not user_data["alliance"]:
            await message.reply("❌ شما در هیچ اتحادی عضو نیستید!")
            return
        
        if target_data["alliance"]:
            await message.reply("❌ این کاربر قبلاً در یک اتحاد عضو است!")
            return
        
        alliance_name = user_data["alliance"]
        alliance_data = game_data["alliances"][alliance_name]
        
        if alliance_data["leader"] != user_id:
            await message.reply("❌ فقط رهبر اتحاد می‌تواند دعوت کند!")
            return
        
        # دعوت کاربر
        await message.reply(f"✅ دعوت به اتحاد '{alliance_name}' برای {target_user.first_name} ارسال شد!")
        
    except Exception as e:
        print(f"خطا در alliance_invite: {e}")
        await message.reply("⚠️ خطا در ارسال دعوت!")

async def alliance_kick(message, chat_id, user_id):
    """اخراج از اتحاد"""
    try:
        if not message.reply_to_message:
            await message.reply("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید!")
            return
        
        target_user = message.reply_to_message.author
        target_user_id = target_user.user_id
        
        user_data = get_user_data(chat_id, user_id)
        target_data = get_user_data(chat_id, target_user_id)
        
        if not user_data["alliance"]:
            await message.reply("❌ شما در هیچ اتحادی عضو نیستید!")
            return
        
        if not target_data["alliance"] or target_data["alliance"] != user_data["alliance"]:
            await message.reply("❌ این کاربر در اتحاد شما عضو نیست!")
            return
        
        alliance_name = user_data["alliance"]
        alliance_data = game_data["alliances"][alliance_name]
        
        if alliance_data["leader"] != user_id:
            await message.reply("❌ فقط رهبر اتحاد می‌تواند اخراج کند!")
            return
        
        if target_user_id == user_id:
            await message.reply("❌ نمی‌توانید خودتان را اخراج کنید!")
            return
        
        # اخراج کاربر
        if target_user_id in alliance_data["members"]:
            alliance_data["members"].remove(target_user_id)
            alliance_data["total_power"] -= calculate_total_power(target_data)
        
        target_data["alliance"] = None
        save_data()
        
        await message.reply(f"✅ کاربر {target_user.first_name} از اتحاد اخراج شد!")
        
    except Exception as e:
        print(f"خطا در alliance_kick: {e}")
        await message.reply("⚠️ خطا در اخراج کاربر!")

async def handle_menu_button(message, button_text, chat_id, user_id):
    """مدیریت دکمه‌های منو"""
    try:
        if button_text == "💰 وضعیت":
            await status_command(message, chat_id, user_id)
        elif button_text == "⚔️ نیروی نظامی":
            await military_command(message, chat_id, user_id)
        elif button_text == "🛒 فروشگاه":
            await shop_command(message, chat_id, user_id)
        elif button_text == "🏰 پایتخت":
            await capital_command(message, chat_id, user_id)
        elif button_text == "🏆 رتبه‌بندی":
            await leaderboard_command(message, chat_id)
        elif button_text == "🤝 اتحاد":
            await alliance_command(message, chat_id, user_id)
        elif button_text == "🕵️ جاسوسی":
            await spy_command(message, chat_id, user_id)
        elif button_text == "🔬 تحقیقات":
            await research_command(message, chat_id, user_id)
        elif button_text == "🤝 دیپلماسی":
            await diplomacy_command(message, chat_id, user_id)
    except Exception as e:
        print(f"خطا در handle_menu_button: {e}")
        await message.reply("⚠️ خطا در پردازش دکمه!")

# ==================== RUN BOT ====================
def main():
    """تابع اصلی اجرای ربات"""
    print("🚀 راه‌اندازی ربات شبیه‌سازی جنگ...")
    print("=" * 50)
    
    # بررسی توکن
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ لطفاً توکن ربات خود را در فایل config.py قرار دهید!")
        print("💡 فایل config_example.py را کپی کرده و نام آن را به config.py تغییر دهید")
        return
    
    # بارگذاری داده‌ها
    load_data()
    print("✅ داده‌ها بارگذاری شد")
    
    # شروع ربات
    print("🤖 ربات در حال راه‌اندازی...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ ربات متوقف شد!")
    except Exception as e:
        print(f"\n❌ خطا در اجرای ربات: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()