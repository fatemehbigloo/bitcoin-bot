import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import os
import time
from collections import deque # برای ذخیره قیمت‌های اخیر

# --- تنظیمات ---
CHECK_INTERVAL_SECONDS = 60  # هر ۶۰ ثانیه (۱ دقیقه) چک کن
PRICE_HISTORY_LENGTH = 5     # قیمت‌های ۵ دقیقه اخیر را نگه دار (هر دقیقه ۱ قیمت)
PRICE_CHANGE_THRESHOLD = 0.03 # حداقل تغییر ۳ درصد برای ارسال پیام

# --- متغیرهای سراسری ---
# استفاده از deque برای نگهداری قیمت‌های اخیر به صورت بهینه
# maxlen=PRICE_HISTORY_LENGTH یعنی حداکثر این تعداد عنصر را نگه می‌دارد
price_history = deque(maxlen=PRICE_HISTORY_LENGTH)
last_sent_price = None # برای جلوگیری از ارسال پیام‌های تکراری در صورت عدم تغییر زیاد

# --- بخش ۱: استخراج قیمت بیت‌کوین از نوبیتکس ---
def get_bitcoin_price_nobitex():
    """
    قیمت فعلی بیت‌کوین را از وب‌سایت نوبیتکس استخراج می‌کند.
    """
    url = "https://nobitex.net/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # بررسی خطاهای HTTP
        soup = BeautifulSoup(response.content, 'html.parser')

        # سلکتور قیمت - این بخش ممکن است نیاز به به‌روزرسانی داشته باشد
        # بر اساس inspect کردن صفحه نوبیتکس
        price_element = soup.find('span', {'class': 'text-body-medium tablet:text-body-large desktop:text-body-large'})

        if not price_element:
            # اگر کلاس بالا پیدا نشد، کلاس دیگری را امتحان کنید
            # price_element = soup.find('p', {'class': 'some-other-price-class'})
            print("هشدار: عنصر قیمت با سلکتور اصلی پیدا نشد. ممکن است ساختار صفحه تغییر کرده باشد.")
            return None

        price_text = price_element.get_text(strip=True)
        price_cleaned = price_text.replace(',', '').replace('تومان', '').strip()
        return float(price_cleaned)

    except requests.exceptions.RequestException as e:
        print(f"خطا در دریافت اطلاعات از نوبیتکس: {e}")
        return None
    except ValueError:
        print(f"مقدار قیمت استخراج شده قابل تبدیل به عدد نیست: '{price_text}'")
        return None
    except Exception as e:
        print(f"خطای غیرمنتظره در استخراج قیمت: {e}")
        return None


# --- بخش ۲: ایجاد و ذخیره نمودار ---
# این تابع همچنان برای نمایش بصری در صورت نیاز مفید است
def create_price_chart(price, filename="bitcoin_price_chart.png"):
    """
    نموداری ساده با قیمت دریافت شده ایجاد و ذخیره می‌کند.
    """
    if price is None:
        print("قیمتی برای رسم نمودار وجود ندارد.")
        return None

    title_text_fa = f"آخرین قیمت: {price:,.0f} تومان"
    reshaped_title = arabic_reshaper.reshape(title_text_fa)
    bidi_title = get_display(reshaped_title)

    plt.figure(figsize=(8, 6))
    plt.bar(['قیمت'], [price], color='skyblue') # استفاده از نام فارسی برای محور

    # اضافه کردن مقدار قیمت به بالای ستون نمودار
    reshaped_val = arabic_reshaper.reshape(f"{price:,.0f} تومان")
    bidi_val = get_display(reshaped_val)
    plt.text('قیمت', price, bidi_val, va='bottom', ha='center')

    plt.title(bidi_title)
    plt.ylabel("قیمت (تومان)")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    chart_path = os.path.join(os.getcwd(), filename)
    try:
        plt.savefig(chart_path, bbox_inches='tight', dpi=100)
        print(f"نمودار با موفقیت در مسیر زیر ذخیره شد: {chart_path}")
        return chart_path
    except Exception as e:
        print(f"خطای در ذخیره نمودار: {e}")
        return None

# --- بخش ۳: مدیریت پیام‌ها و ارسال به بله ---
# این تابع باید با API بات بله شما ادغام شود
# فرض می‌کنیم تابعی به نام `send_bale_message` وجود دارد که پیام را ارسال می‌کند
def send_bale_message(text):
    """
    یک تابع نمونه برای ارسال پیام به بله.
    شما باید این را با کد واقعی ارسال پیام بات خود جایگزین کنید.
    """
    print(f"--- ارسال پیام به بله ---")
    print(text)
    print(f"------------------------")
    # در کد واقعی، اینجا باید از کتابخانه یا API بله برای ارسال پیام استفاده کنید.
    # مثال:
    # bot_token = "YOUR_NEW_BALE_BOT_TOKEN"
    # chat_id = "YOUR_CHAT_ID" # آیدی چت کاربر یا گروه
    # url = f"https://tapi.bale.ai/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}"
    # response = requests.get(url)
    # if response.status_code == 200:
    #     print("پیام با موفقیت ارسال شد.")
    # else:
    #     print(f"خطا در ارسال پیام: {response.status_code} - {response.text}")
    # در اینجا فقط چاپ می‌کنیم تا کد قابل اجرا باشد
    return True # فرض می‌کنیم ارسال موفق بوده

def check_price_and_notify():
    """
    قیمت را چک می‌کند، تغییرات را محاسبه و در صورت لزوم پیام ارسال می‌کند.
    """
    global price_history, last_sent_price

    current_price = get_bitcoin_price_nobitex()

    if current_price is None:
        print("خطا در دریافت قیمت، از تلاش بعدی صرف نظر می‌کنیم.")
        return

    print(f"قیمت فعلی دریافت شد: {current_price:,.0f} تومان")

    # اضافه کردن قیمت فعلی به تاریخچه
    price_history.append(current_price)

    # اگر تاریخچه به اندازه کافی پر نشده باشد (حداقل ۲ قیمت برای مقایسه)
    if len(price_history) < 2:
        print("در حال جمع‌آوری داده‌های اولیه قیمت...")
        # نمودار آخرین قیمت را هم رسم می‌کنیم
        create_price_chart(current_price, filename="latest_price.png")
        return

    # گرفتن قیمت ۵ دقیقه قبل (اولین قیمت در deque اگر طول آن برابر maxlen باشد)
    # یا آخرین قیمتی که قبل از قیمت فعلی اضافه شده است.
    # برای دقیق‌تر بودن، به آخرین قیمت قبل از فعلی نیاز داریم.
    # اگر len(price_history) == PRICE_HISTORY_LENGTH باشد، یعنی قیمت قبلی داریم
    # اگر len(price_history) < PRICE_HISTORY_LENGTH باشد، یعنی هنوز ۵ قیمت نداریم
    # در هر دو صورت، برای محاسبه تغییر 3% به قیمت 5 دقیقه قبل نیاز داریم.

    # یافتن قیمت مربوط به 5 دقیقه قبل
    # از آنجایی که deque قیمت‌ها را پشت سر هم نگه می‌دارد،
    # اگر maxlen=5 باشد، عنصر اول (index 0) قدیمی‌ترین قیمت و عنصر آخر (index -1) جدیدترین است.
    # ما به قیمت 5 دقیقه قبل نیاز داریم، که اگر هر دقیقه یک بار چک کنیم،
    # اولین عنصر price_history (اگر طولش 5 باشد) قیمت 5 دقیقه قبل است.
    # اما اگر طول کمتر از 5 باشد، چه؟
    # برای سادگی، از آخرین قیمت موجود در تاریخچه که *قبل* از قیمت فعلی بوده استفاده می‌کنیم.
    # اگر تاریخچه ما [100, 105, 110] باشد و قیمت جدید 115 باشد، قیمت "قبلی" 110 است.
    # اما برای محاسبه 3% نسبت به 5 دقیقه قبل، باید به اولین عنصر deque (اگر طولش 5 باشد) نگاه کنیم.

    # اگر تاریخچه کامل نیست (کمتر از 5 قیمت)، از آخرین قیمت موجود به عنوان مبنا استفاده می‌کنیم
    if len(price_history) < PRICE_HISTORY_LENGTH:
         previous_price_5min_ago = price_history[0] # اولین عنصری که اضافه شده
    else:
         # اگر تاریخچه کامل است (5 قیمت)، اولین عنصر، قیمت 5 دقیقه قبل است
         previous_price_5min_ago = price_history[0]

    if previous_price_5min_ago is None or previous_price_5min_ago == 0:
         print("قیمت قبلی نامعتبر است، امکان محاسبه تغییرات وجود ندارد.")
         # اگر قیمت قبلی نامعتبر است، نمودار قیمت فعلی را رسم می‌کنیم
         create_price_chart(current_price, filename="latest_price.png")
         return

    # محاسبه درصد تغییر
    price_difference = current_price - previous_price_5min_ago
    price_change_percentage = (price_difference / previous_price_5min_ago)

    print(f"قیمت ۵ دقیقه قبل: {previous_price_5min_ago:,.0f}")
    print(f"تغییر قیمت: {price_difference:,.0f} ({price_change_percentage:.2%})")

    # بررسی شرط ارسال پیام
    # اگر تغییر بیشتر از حد آستانه بود و همچنین از آخرین پیامی که ارسال کردیم
    # تغییر قابل توجهی داشته باشد (برای جلوگیری از پیام‌های تکراری)
    send_notification = False
    message_text = ""

    if abs(price_change_percentage) >= PRICE_CHANGE_THRESHOLD:
        if last_sent_price is None or abs(current_price - last_sent_price) / current_price > 0.01: # مثلاً اگر ۱% هم فرق کرده باشد
            if price_change_percentage > 0:
                # قیمت بالا رفته
                message_text = f"📈 قیمت بیت‌کوین افزایش یافت!\nقیمت جدید: {current_price:,.0f} تومان\n(تغییر نسبت به ۵ دقیقه قبل: {price_change_percentage:.2%})"
            else:
                # قیمت پایین آمده
                message_text = f"📉 قیمت بیت‌کوین کاهش یافت!\nقیمت جدید: {current_price:,.0f} تومان\n(تغییر نسبت به ۵ دقیقه قبل: {price_change_percentage:.2%})"
            send_notification = True
            last_sent_price = current_price # به‌روزرسانی آخرین قیمتی که پیامش ارسال شده

    if send_notification:
        # ارسال پیام به بله
        if send_bale_message(message_text):
            print("پیام هشدار تغییر قیمت با موفقیت ارسال شد.")
        else:
            print("خطا در ارسال پیام هشدار تغییر قیمت.")

    # رسم نمودار قیمت فعلی (برای نمایش لحظه‌ای)
    create_price_chart(current_price, filename="latest_price.png")


# --- حلقه اصلی برنامه ---
