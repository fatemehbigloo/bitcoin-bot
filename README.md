# bitcoin-bot
first, please read file that name is " read-it.txt " , then run app.py

# 🤖 Bitcoin Bot - Bitcoin Price Monitoring Bot

An automated bot that receives the Bitcoin price from the Nobitex site, monitors changes, and notifies the user via **Yes Messenger Bot** if it changes more than 3%.

A **Flask web server** is also provided for status display and easy access.

## 📋 Prerequisites
- Python 3.8 or higher
- Internet connection (to get prices and send messages)
- Robot Token Yes (to send messages and photos)

📁 Project Structure
Explanation File
app.py Main Application File - Setting Up Threads and Web Server
cal_photo_creation.py Get Prices, Compare, Create Charts, and Send Notifications
database.py Manage Database and Check User Registration
sen_sms.py Send Messages and Photos via API Yes

📝 File Description

cal_photo_creation.py

· Get ​​the current Bitcoin price from Nobitex
· Compare the price with the previous 5 minutes
· Send a notification if the price changes by more than 3%
· Keep the history of the last 5 prices in memory
· Save the price chart as latest_price.png

database.py
· Get ​​chat_id from the input
· Connect to the SQLite database
· Check if chat_id exists in the users table
· Return True if it exists, False otherwise

sen_sms.py

send_bale_message - Send text message

· Get ​​token, user/group ID and message text
· Send request to API Yes (https://tapi.bale.ai)
· Return JSON response if successful

send_bale_photo - Send photo (price chart)

· Get ​​token, user ID, file path and optional caption
· Send file as binary to API Yes
· Return JSON response if successful

app.py
1. Start price receiving thread - Checks price every few minutes
2. Start bot thread - Connects to server Yes and responds to messages
3. Run Flask web server - On port 8000 and in debug=False mode

👨‍💻 Developer
[Fatemeh Bigloo] - [ghasembigloo5@gmail.com]


