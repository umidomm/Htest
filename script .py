import os
import json
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import random
import arabic_reshaper
from bidi.algorithm import get_display

# مسیر فونت و لوگو را تنظیم کنید
font_path = 'vazir.ttf'
logo_path = 'logo.png'

# فونت فارسی را ثبت کنید
pdfmetrics.registerFont(TTFont('Vazir', font_path))

# سبک پاراگراف را تنظیم کنید
styles = getSampleStyleSheet()
style = styles['Normal']
style.fontName = 'Vazir'
style.fontSize = 14
style.leading = 18
style.alignment = 2

# سبک پاراگراف جدید برای ردیف‌های 'Usage Limit' و 'Start Date'
style_data = ParagraphStyle('DataStyle')
style_data.fontName = 'Vazir'
style_data.fontSize = 12
style_data.leading = 14

# سبک پاراگراف جدید برای ردیف 'UUID'
style_uuid = ParagraphStyle('UUIDStyle')
style_uuid.fontName = 'Vazir'
style_uuid.fontSize = 10
style_uuid.leading = 12

# تابع برای تبدیل متن فارسی به فرمت قابل نمایش
def format_persian_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# تابع برای خواندن داده‌ها از فایل JSON و بازگرداندن لیست کاربران و ادمین‌ها
def read_users_from_backup(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data.get('users', []), data.get("admin_users", [])

# تابع برای نوشتن اطلاعات کاربران به فایل PDF
def write_users_to_pdf(users, admin_name, user_date):
    min_number = 10000
    max_number = 99999
    random_number = random.randint(min_number, max_number)
    file_name = f"/media/{admin_name}_{random_number}.pdf"
    pdf = SimpleDocTemplate(file_name, pagesize=letter)
    elements = []

    # اضافه کردن لوگو
    logo = Image(logo_path)
    logo.drawHeight = 2 * inch  # افزایش ارتفاع لوگو به دو برابر
    logo.drawWidth = 4 * inch   # افزایش عرض لوگو به دو برابر
    elements.append(logo)
    elements.append(Spacer(1, 12))

    table_data = [['UUID', 'Start Date', 'Usage Limit (GB)', 'Package Days', 'Name']]
    total_usage_limit = 0
    
    for user in users:
        start_date_str = user.get('start_date')
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                if start_date >= user_date:
                    user_name = user.get('name', '')
                    name_paragraph = Paragraph(format_persian_text(user_name), style)
                    uuid_paragraph = Paragraph(format_persian_text(user['uuid']), style_uuid)
                    usage_limit = user.get('usage_limit_GB', 0)
                    package_days = user.get('package_days', 0)
                    start_date_paragraph = Paragraph(format_persian_text(start_date_str), style_data)
                    usage_limit_paragraph = Paragraph(format_persian_text(str(usage_limit)), style_data)
                    package_days_paragraph = Paragraph(format_persian_text(str(package_days)), style_data)
                    table_data.append([uuid_paragraph, start_date_paragraph, usage_limit_paragraph, package_days_paragraph, name_paragraph])
                    total_usage_limit += usage_limit
            except Exception as e:
                continue
    
    total_usage_paragraph = Paragraph(format_persian_text(str(total_usage_limit)), style_data)
    table_data.append(['', '', total_usage_paragraph, '', 'total usage'])
    col_widths = [2.5 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 2.0 * inch]
    table = Table(table_data, colWidths=col_widths)
    style_table = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkslategray),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Vazir'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BOX',(0,0),(-1,-1),2,colors.black)])
    
    # تنظیم رنگ‌بندی یکی در میان برای ردیف‌های جدول
    for i in range(1, len(table_data), 2):
        style_table.add('BACKGROUND', (0,i), (-1,i), colors.navajowhite)
    
    table.setStyle(style_table)
    elements.append(table)
    pdf.build(elements)

# تابع اصلی
def main():
    backup_directory = "/opt/hiddify-manager/hiddify-panel/backup"
    
    while True:
        print("لطفاً یکی از گزینه‌های زیر را انتخاب کنید:")
        print("1. Daily")
        print("2. Weekly")
        print("3. Monthly")
        print("4. All the time")
        print("5. Enter the date")
        print("6. Exit")
        
        choice = input("گزینه مورد نظر را وارد کنید: ")
        
        if choice == '1':
            user_date = datetime.now().date() - timedelta(days=1)
        elif choice == '2':
            user_date = datetime.now().date() - timedelta(weeks=1)
        elif choice == '3':
            user_date = datetime.now().date() - timedelta(days=30)
        elif choice == '4':
            user_date = datetime.min.date()
        elif choice == '5':
            date_entry = input('لطفاً تاریخ شروع استفاده کاربران را وارد کنید (به فرمت YYYY-MM-DD): ')
            user_date = datetime.strptime(date_entry, '%Y-%m-%d').date()
        elif choice == '6':
            print("خروج از برنامه.")
            break
        else:
            print("گزینه نامعتبر است. لطفاً دوباره تلاش کنید.")
            continue

        json_files = [f for f in os.listdir(backup_directory) if f.endswith('.json')]
        if not json_files:
            print("No JSON backup files found.")
            return
        
        latest_backup_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(backup_directory, f)))
        file_path = os.path.join(backup_directory, latest_backup_file)
        
        users, admin_users = read_users_from_backup(file_path)
        if users:
            for admin in admin_users:
                admin_name = admin.get("name", "")
                admin_users_list = [user for user in users if user["added_by_uuid"] == admin["uuid"] and user.get('start_date')]
                write_users_to_pdf(admin_users_list, admin_name, user_date)
        break

if __name__ == "__main__":
    main()