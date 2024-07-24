from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("MY_TWILIO_NUMBER")
VERIFIED_NUMBER = os.getenv("RECIPIENT_NUMBER")

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
PRICE_CHANGE_PERCENTAGE = 2

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stock', methods=['GET'])
def get_stock_news():
    stock_name = request.args.get('stock')
    news_query = stock_name

    stocks_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_name,
        "apikey": STOCK_API_KEY
    }

    stock_response = requests.get(url=STOCK_ENDPOINT, params=stocks_parameters)
    stock_data = stock_response.json()

    if "Time Series (Daily)" not in stock_data:
        return jsonify({"error": "Stock data not found"}), 404

    data = stock_data["Time Series (Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_closing_price = data_list[0]["4. close"]
    day_before_yesterday_closing_price = data_list[1]["4. close"]

    difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
    up_down = "🔺" if difference > 0 else "🔻"
    diff_percent = round((difference / float(day_before_yesterday_closing_price)) * 100, 2)

    if abs(diff_percent) > PRICE_CHANGE_PERCENTAGE:
        news_parameters = {
            "q": news_query,
            "apiKey": NEWS_API_KEY,
        }
        news_response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
        news_data = news_response.json()
        articles = news_data.get("articles", [])[:3]

        # Format the articles
        formatted_articles = [
            f"{stock_name}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in articles
        ]

        # Send a message via Twilio for each article
        for article in formatted_articles:
            message = client.messages.create(
                body=article,
                from_=TWILIO_NUMBER,
                to=VERIFIED_NUMBER
            )

        return jsonify({
            "stock": stock_name,
            "up_down": up_down,
            "diff_percent": diff_percent,
            "articles": articles
        })
    else:
        return jsonify({
            "stock": stock_name,
            "up_down": up_down,
            "diff_percent": diff_percent,
            "articles": []
        })

if __name__ == '__main__':
    app.run(debug=True)


    
