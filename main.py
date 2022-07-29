from telebot import types
from config import *
from datetime import datetime
from binance import Client
import os
import telebot

class BuySellBot():
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv('BuySellCrypto'))
        self.client = Client(API_KEY, SECRET_KEY, testnet=True)
        self.cryptos = ["BTC", "ETH", "BNB", "USDT"]
        self.side = None
        self.crypto = None
        self.quantity = None

    def check_balance(self, symbol):
        try:
            return self.client.get_asset_balance(asset=symbol)
        except Exception as ex:
            print(f"***Exception: {ex}***")

    def current_price(self, symbol):
        try:
            return self.client.get_avg_price(symbol=symbol + "USDT")["price"]
        except Exception as ex:
            print(f"***Exception: {ex}***")

    def display_prices(self, message):
        answer_date = "Date: " + datetime.now().strftime("%Y-%m-%d") + "\n" + \
                      "Time: " + datetime.now().strftime("%H:%M:%S")

        answer_crypto = ""
        num = 0
        for crypto in self.cryptos[:-1]:
            price = self.current_price(crypto)
            answer_crypto += f"{self.cryptos[:-1][num]}: {round(float(price), 3)}$\n"

            num += 1

        self.bot.send_message(message.chat.id, answer_date)
        self.bot.send_message(message.chat.id, answer_crypto)

        self.side = None
        self.crypto = None
        self.quantity = None

    def display_balance(self, message):
        answer_date = "Date: " + datetime.now().strftime("%Y-%m-%d") + "\n" + \
                 "Time: " + datetime.now().strftime("%H:%M:%S")

        answer_crypto = ""
        for crypto in self.cryptos:
            balance = self.check_balance(crypto)
            answer_crypto += f"{balance['asset']}: {round(float(balance['free']), 3)}\n"

        self.bot.send_message(message.chat.id, answer_date)
        self.bot.send_message(message.chat.id, answer_crypto)

        self.side = None
        self.crypto = None
        self.quantity = None

    def buy_order(self, message, symbol, quantity):
        try:
            amount = float(quantity) * round(float(self.current_price(symbol)), 3)
            if amount <= float(self.check_balance("USDT")["free"]):
                self.client.order_market_buy(symbol=symbol + "USDT", quantity=quantity)
                self.bot.send_message(message.chat.id, "The order was successfully completed!")

            else:
                self.bot.send_message(message.chat.id, "Not enough USDT!")

            self.display_main_button(message)
            self.side = None
            self.crypto = None
            self.quantity = None
        except Exception as ex:
            print(f"***Exception: {ex}***")

    def sell_order(self, message, symbol, quantity):
        try:
            if float(quantity) <= float(self.check_balance(symbol)["free"]):
                self.client.order_market_sell(symbol=symbol + "USDT", quantity=quantity)
                self.bot.send_message(message.chat.id, "The order was successfully completed!")

            else:
                self.bot.send_message(message.chat.id, f"Not enough {symbol}!")

            self.display_main_button(message)
            self.side = None
            self.crypto = None
            self.quantity = None
        except Exception as ex:
            print(f"***Exception: {ex}***")

    def display_main_button(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("BUY"),
                   types.KeyboardButton("PRICES"),
                   types.KeyboardButton("SELL"),
                   types.KeyboardButton("BALANCE"))

        self.bot.send_message(message.chat.id, "Choose the side!", reply_markup=markup)

    def display_crypto_button(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("BTC"),
                   types.KeyboardButton("ETH"),
                   types.KeyboardButton("BNB"))

        self.bot.send_message(message.chat.id, "Choose the crypto!", reply_markup=markup)

    def determine_way(self, message, text, quantity):
        if self.side == "BUY":
            self.buy_order(message, text, quantity)

        elif self.side == "SELL":
            self.sell_order(message, text, quantity)

    def bot_message(self):
        @self.bot.message_handler(commands=["start"])
        def start_message(message):
            self.bot.send_message(message.chat.id, "Hello, BOT!\nI buy and sell crypto!")
            self.display_main_button(message)

        @self.bot.message_handler(commands=["retry"])
        def start_message(message):
            self.display_main_button(message)

        @self.bot.message_handler(content_types=["text"])
        def send_text(message):
            try:
                text = message.text.strip().upper()
                if text == "BUY":
                    self.side = "BUY"
                    self.display_crypto_button(message)

                elif text == "SELL":
                    self.side = "SELL"
                    self.display_crypto_button(message)

                elif text == "BALANCE":
                    self.side = "BALANCE"
                    self.display_balance(message)

                elif text == "PRICES":
                    self.side = "PRICES"
                    self.display_prices(message)

                elif text == "BTC" and self.side is not None:
                    self.crypto = "BTC"
                    self.bot.send_message(message.chat.id, "Enter quantity!")

                elif text == "ETH" and self.side is not None:
                    self.crypto = "ETH"
                    self.bot.send_message(message.chat.id, "Enter quantity!")

                elif text == "BNB" and self.side is not None:
                    self.crypto = "BNB"
                    self.bot.send_message(message.chat.id, "Enter quantity!")

                elif message.text.replace('.', '', 1).isdigit() and self.side is not None and self.crypto is not None:
                    self.quantity = float(text)
                    self.determine_way(message, self.crypto, self.quantity)

                else:
                    self.bot.send_message(message.chat.id, "Please, first of all, choose side then the crypto and the quantity!")

            except Exception as ex:
                print(f"***Exception: {ex}***")

        self.bot.infinity_polling()

if __name__ == '__main__':
    print("Program started!")
    BOT = BuySellBot()
    BOT.bot_message()
    print("***Program Never Ended!!!***\nBut...\n ):If you see this message, it was ended:(")

