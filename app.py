from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi
import config
import json

app = Flask(__name__)

api = tradeapi.REST(config.API_KEY, config.API_SECRET,
                    base_url='https://paper-api.alpaca.markets', api_version='v2')


@app.route('/')
def dashboard():
    orders = api.list_orders()
    positions = api.list_positions()
    print(orders)
    return render_template('dashboard.html', alpaca_orders=orders, alpaca_positions=positions)


@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)
    print(webhook_message)
    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }

    # limit_price = webhook_message['strategy'].get('limit_price', None)
    # stop_price = webhook_message['strategy'].get('stop_price', None)
    # quantity = webhook_message['strategy']['order_quantity']
    # symbol = webhook_message['ticker']
    # side = webhook_message['strategy']['order_action']

    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    # quantity = webhook_message['strategy']['order_quantity']
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    order_type = webhook_message['strategy']['order_type']
    print(order_type)
    if side not in ['buy', 'sell']:
        return "Invalid order side"

    if order_type not in ['market', 'limit', 'stop']:
        order = api.submit_order(
            symbol, quantity, side, 'market', 'gtc')
    elif order_type in ['limit']:
        order = api.submit_order(
            symbol, quantity, side, 'limit', 'gtc', limit_price=price)
    elif order_type in ['stop']:
        order = api.submit_order(
            symbol, quantity, side, 'stop', 'gtc')
    else:
        # "invalid order type"
        order = api.submit_order(
            symbol, quantity, side, 'market', 'gtc')

    # try:
    #     order = submit_order(symbol, quantity, side,
    #                          order_type, 'gtc', limit_price, stop_price)
    #     print(order)
    # except tradeapi.rest.APIError as e:
    #     if "invalid side" in str(e):
    #         return "Invalid order side"
    #     else:
    #         # handle other API errors
    #         return f"Error submitting order: {str(e)}"

    return webhook_message


def submit_order(symbol, quantity, side, order_type, time_in_force, limit_price=None, stop_price=None):
    order_parameters = {
        'symbol': symbol,
        'qty': quantity,
        'side': side,
        'type': order_type,
        'time_in_force': time_in_force
    }

    if order_type == 'limit':
        order_parameters['limit_price'] = limit_price
    elif order_type == 'stop':
        order_parameters['stop_price'] = stop_price

    order = api.submit_order(**order_parameters)
    return order
