import requests

def send_bale_message(token, chat_id, text):
    url = f"https://tapi.bale.ai/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        print("پیام با موفقیت ارسال شد!")
        print(response.text)
        return response.json()
    except Exception as e:
        print(f"یک خطا رخ داد: {e}")
        return None


def send_bale_photo(token, chat_id, photo_path, caption="نمودار قیمت بیت‌کوین"):
    url = f"https://tapi.bale.ai/bot{token}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, data=data, files=files, timeout=15)
            response.raise_for_status()
            print("عکس با موفقیت ارسال شد!")
            return response.json()
    except Exception as e:
        print(f"خطا در ارسال عکس: {e}")
        return None
