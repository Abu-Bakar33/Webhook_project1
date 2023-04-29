from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi
import config
import json

app = Flask(__name__)

api = tradeapi.REST(config.API_KEY, config.API_SECRET,
                    base_url='https://paper-api.alpaca.markets', api_version='v2')

# This is url to show the dashboard


@app.route('/')
def dashboard():
    orders = api.list_orders()
    print(orders)

    return render_template('dashboard.html', alpaca_orders=orders)


# This is the route url  that we will send our data to webhook to  and it will send it to alpaca


@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }

    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']

    # print(f"Side: {side}")
    # order = api.submit_order(symbol, quantity, side,
    #                          'limit', 'gtc', limit_price=price)
    try:
        order = api.submit_order(
            symbol, quantity, side, 'limit', 'gtc', limit_price=price)
    # except APIError as e:
    except tradeapi.rest.APIError as e:
        if "invalid side" in str(e):
            return "Invalid order side"
        else:
            # handle other API errors
            return "Error submitting order"

    # print(order)
    return webhook_message
# print(webhook())
