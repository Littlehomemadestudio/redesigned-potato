# Dockerfile for War Simulation Bot
FROM python:3.9-slim

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ایجاد دایرکتوری کار
WORKDIR /app

# کپی فایل‌های مورد نیاز
COPY requirements.txt .
COPY war_simulation_bot.py .
COPY test_bot.py .
COPY run.py .
COPY config_example.py .

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# ایجاد دایرکتوری برای داده‌ها
RUN mkdir -p /app/data

# تنظیم مجوزها
RUN chmod +x run.py

# اجرای ربات
CMD ["python", "run.py"]