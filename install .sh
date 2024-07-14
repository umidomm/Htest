#!/bin/bash

# نصب کتابخانه‌های مورد نیاز
pip install reportlab arabic_reshaper python-bidi

# دانلود فونت و لوگو از مخزن GitHub
curl -O https://raw.githubusercontent.com/umidomm/Htest/main/Vazir.ttf
curl -O https://raw.githubusercontent.com/umidomm/Htest/main/logo.png

# دانلود اسکریپت پایتون
curl -O https://raw.githubusercontent.com/umidomm/Htest/main/script.py

# اجرای اسکریپت پایتون
python script.py
