import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from sen_sms import send_bale_message, send_bale_photo
from database import init_db, save_price, get_last_price, get_all_prices, save_chat_id, get_all_chat_ids, is_user_registered
import matplotlib.pyplot as plt

# تنظیمات بات - این مقادیر را مستقیم قرار دادم
# اگر می‌خواهید از متغیرهای محیطی استفاده کنید، باید آن‌ها را در سیستم یا هاست خود تعریف کنید
MY_TOKEN = "513571946:Ppp8Er_cpfVeYaYw_56hriMbVn6CWLDZkHc" 
# MY_CHAT_ID = "666417472" # این متغیر الان در fetch_price_worker به صورت مستقیم استفاده نمیشه، بلکه از دیتابیس گرفته میشه

app = Flask(__name__)
init_db()  # راه‌اندازی دیتابیس

def fetch_price_worker():
    """وظیفه پس‌زمینه برای دریافت قیمت و ارسال به کاربران ثبت‌شده"""
    url = "https://nobitex.ir/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            # دقت کن که سلکتور باید درست باشه. این سلکتور ممکنه تغییر کنه.
            element = soup.select_one("span.text-body-medium.tablet\\:text-body-large.desktop\\:text-body-large") 
            
            if element:
                new_price_str = element.get_text(strip=True).replace(",", "")
                if not new_price_str: # اگر قیمت خالی بود، رد شو
                    print("قیمت دریافت نشد.")
                    time.sleep(300)
                    continue

                new_price = float(new_price_str)
                last_price = get_last_price()
                
                # ذخیره قیمت جدید در دیتابیس
                save_price(new_price)
                print(f"قیمت ثبت شد: {new_price}")

                # ارسال پیام به همه کاربران ثبت شده
                chat_ids = get_all_chat_ids()
                if chat_ids:
                    for chat_id in chat_ids:
                        # فقط اگر کاربر ثبت شده است، پیام را ارسال کن
                        if is_user_registered(chat_id): 
                            if last_price:
                                if new_price < last_price:
                                    message = f"📉 قیمت اومد پایین!\nقیمت جدید: {new_price:,.0f} تومان"
                                elif new_price > last_price:
                                    message = f"📈 قیمت رفت بالا!\nقیمت جدید: {new_price:,.0f} تومان"
                                else: # قیمت تغییری نکرده
                                    continue 
                            else: # اگر اولین قیمته
                                message = f"🚀 قیمت اولیه ثبت شد:\n{new_price:,.0f} تومان"
                            
                            send_bale_message(MY_TOKEN, chat_id, message)
                            time.sleep(1) # برای جلوگیری از بلاک شدن توسط API بله
                else:
                    print("هیچ کاربری برای ارسال قیمت یافت نشد.")

            else:
                print("عنصر قیمت در صفحه یافت نشد.")
        
        except requests.exceptions.RequestException as e:
            print(f"خطای شبکه در دریافت قیمت: {e}")
        except ValueError:
            print(f"خطای تبدیل قیمت به عدد: '{new_price_str}'")
        except Exception as e:
            print(f"خطای غیرمنتظره در fetch_price_worker: {e}")
        
        time.sleep(300)  # وقفه ۵ دقیقه

def generate_chart():
    """تولید نمودار قیمت"""
    prices = get_all_prices()
    if not prices:
        print("دیتابیس قیمت خالی است، نمودار تولید نمی‌شود.")
        return False # نشان می‌دهد که نمودار تولید نشده

    try:
        plt.figure(figsize=(10, 5))
        plt.plot(prices, marker='o', linestyle='-', color='blue')
        plt.title("BTC Price Trend")
        plt.xlabel("Time (Entries)") # برچسب محور افقی را کمی واضح‌تر کردیم
        plt.ylabel("Price (Toman)")
        plt.grid(True)
        
        # ذخیره نمودار
        chart_path = 'img\chart.png'
        plt.savefig(chart_path)
        plt.close() 
        print(f"نمودار در مسیر {chart_path} ذخیره شد.")
        return chart_path # مسیر فایل نمودار را برمی‌گردانیم
    except Exception as e:
        print(f"خطا در تولید نمودار: {e}")
        return False

def bot_polling():
    """پولینگ بات برای دریافت دستورات"""
    offset = 0
    print("بات فعال شد و در حال گوش دادن به پیام‌هاست...")
    while True:
        try:
            # استفاده از MY_TOKEN برای ارتباط با API بله
            url = f"https://tapi.bale.ai/bot{MY_TOKEN}/getUpdates?offset={offset}"
            response = requests.get(url, timeout=10)
            response.raise_for_status() # بررسی خطاهای HTTP
            updates = response.json()
            
            if updates.get('ok') and updates.get('result'):
                for update in updates['result']:
                    update_id = update['update_id']
                    offset = update_id + 1 # به‌روزرسانی آفست برای دریافت پیام‌های بعدی
                    
                    message = update.get('message')
                    if not message:
                        continue

                    chat_id = message.get('chat', {}).get('id')
                    text = message.get('text', '')
                    
                    # همیشه chat_id را ذخیره کن تا کاربرانی که پیام می‌دهند، ثبت شوند
                    if chat_id:
                        save_chat_id(chat_id) 
                    
                    # پردازش دستورات
                    if text.lower() == "/start":
                        welcome_message = "به ربات قیمت بیت‌کوین خوش آمدید!\nبا دستور /chart می‌توانید نمودار قیمت را دریافت کنید."
                        send_bale_message(MY_TOKEN, chat_id, welcome_message)
                        print(f"کاربر {chat_id} با /start شروع کرد.")
                    
                    elif text.lower() == "/chart":
                        print(f"دستور /chart از کاربر {chat_id} دریافت شد!")
                        chart_path = generate_chart() 
                        if chart_path:
                            send_bale_photo(MY_TOKEN, chat_id, chart_path, "نمودار قیمت بیت‌کوین")
                        else:
                            send_bale_message(MY_TOKEN, chat_id, "متاسفانه امکان تولید نمودار وجود ندارد (ممکن است دیتابیس خالی باشد).")
            
        except requests.exceptions.RequestException as e:
            print(f"خطای شبکه در پولینگ: {e}")
            time.sleep(5) # اگر خطا در شبکه بود، کمی بیشتر صبر کن
        except Exception as e:
            print(f"خطای غیرمنتظره در bot_polling: {e}")
            # آفست را اینجا به‌روزرسانی نکن تا پیام‌های قبلی دوباره پردازش نشوند، مگر اینکه مطمئن باشی خطا مربوط به آفست نیست
            # offset = update_id + 1 # اگر خطا مربوط به پیام خاصی بود
        
        # time.sleep(2) # این sleep در حلقه اصلی پولینگ حذف شد تا با آفست دقیق‌تر کار کند

# روت برای چک کردن آخرین قیمت از طریق مرورگر
@app.route("/btc", methods=["GET"])
def get_btc():
    last_price = get_last_price()
    if last_price:
        # فرمت‌بندی قیمت با کاما و دو رقم اعشار
        formatted_price = f"{last_price:,.2f}" 
        return jsonify({"last_price": formatted_price})
    else:
        return jsonify({"message": "هنوز قیمتی ثبت نشده است."}), 404

if __name__ == '__main__':
    print("در حال راه‌اندازی بات و وب‌سرور...")
    
    # راه‌اندازی ترد دریافت قیمت در پس‌زمینه
    # daemon=True یعنی اگر برنامه اصلی بسته شد، این ترد هم بسته شود
    price_thread = threading.Thread(target=fetch_price_worker, daemon=True)
    price_thread.start()
    
    # راه‌اندازی ترد پولینگ بات در پس‌زمینه
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()
    
    # اجرای وب‌سرور فلَسک در ترد اصلی
    # اگر این ترد بسته شود، برنامه هم بسته می‌شود
    print("وب‌سرور Flask در حال اجرا روی http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=False) # debug=False برای تولید
