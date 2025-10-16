# Makefile for War Simulation Bot

.PHONY: help install test run clean docker-build docker-run docker-stop

# متغیرهای پیش‌فرض
PYTHON = python3
PIP = pip3
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# راهنمای استفاده
help:
	@echo "دستورات موجود:"
	@echo "  install      - نصب وابستگی‌ها"
	@echo "  test         - اجرای تست‌ها"
	@echo "  run          - اجرای ربات"
	@echo "  clean        - پاکسازی فایل‌های موقت"
	@echo "  docker-build - ساخت تصویر داکر"
	@echo "  docker-run   - اجرای ربات با داکر"
	@echo "  docker-stop  - توقف ربات داکر"
	@echo "  setup        - راه‌اندازی کامل"

# نصب وابستگی‌ها
install:
	@echo "📦 نصب وابستگی‌ها..."
	$(PIP) install -r requirements.txt
	@echo "✅ وابستگی‌ها نصب شد!"

# اجرای تست‌ها
test:
	@echo "🧪 اجرای تست‌ها..."
	$(PYTHON) test_bot.py
	@echo "✅ تست‌ها کامل شد!"

# اجرای ربات
run:
	@echo "🚀 اجرای ربات..."
	$(PYTHON) run.py

# پاکسازی فایل‌های موقت
clean:
	@echo "🧹 پاکسازی فایل‌های موقت..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "test_data.txt" -delete
	@echo "✅ پاکسازی کامل شد!"

# ساخت تصویر داکر
docker-build:
	@echo "🐳 ساخت تصویر داکر..."
	$(DOCKER) build -t war-simulation-bot .
	@echo "✅ تصویر داکر ساخته شد!"

# اجرای ربات با داکر
docker-run:
	@echo "🐳 اجرای ربات با داکر..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ ربات با داکر اجرا شد!"

# توقف ربات داکر
docker-stop:
	@echo "🐳 توقف ربات داکر..."
	$(DOCKER_COMPOSE) down
	@echo "✅ ربات داکر متوقف شد!"

# راه‌اندازی کامل
setup: install
	@echo "🔧 راه‌اندازی کامل..."
	@if [ ! -f config.py ]; then \
		echo "📝 ایجاد فایل تنظیمات..."; \
		cp config_example.py config.py; \
		echo "⚠️ لطفاً فایل config.py را ویرایش کرده و توکن ربات خود را قرار دهید!"; \
	fi
	@echo "✅ راه‌اندازی کامل شد!"
	@echo "💡 برای اجرای ربات از دستور 'make run' استفاده کنید"

# نمایش وضعیت
status:
	@echo "📊 وضعیت ربات:"
	@echo "  فایل config.py: $$(if [ -f config.py ]; then echo '✅ موجود'; else echo '❌ موجود نیست'; fi)"
	@echo "  فایل war_data.txt: $$(if [ -f war_data.txt ]; then echo '✅ موجود'; else echo '❌ موجود نیست'; fi)"
	@echo "  فایل war_logs.txt: $$(if [ -f war_logs.txt ]; then echo '✅ موجود'; else echo '❌ موجود نیست'; fi)"
	@echo "  وابستگی‌ها: $$(if $(PIP) show bale-python > /dev/null 2>&1; then echo '✅ نصب شده'; else echo '❌ نصب نشده'; fi)"