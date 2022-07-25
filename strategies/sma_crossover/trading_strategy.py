import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
from account_credentials import LOGIN, PASSWORD, SERVER

symbol = 'DE40'
timeframe = mt5.TIMEFRAME_M5
volume = 0.5
strategy_name = 'ma_trendfollowing'


def get_sma(symbol, timeframe, period):
    sma = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timeframe, 1, period))['close'].mean()

    return sma


def close_position(position, deviation=20, magic=12345):

    order_type_dict = {
        0: mt5.ORDER_TYPE_SELL,
        1: mt5.ORDER_TYPE_BUY
    }

    price_dict = {
        0: mt5.symbol_info_tick(symbol).bid,
        1: mt5.symbol_info_tick(symbol).ask
    }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position['ticket'],  # select the position you want to close
        "symbol": symbol,
        "volume": volume,  # FLOAT
        "type": order_type_dict[position['type']],
        "price": price_dict[position['type']],
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": strategy_name,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    return(order_result)


def close_positions(order_type):
    order_type_dict = {
        'buy': 0,
        'sell': 1
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get()

        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())

        if order_type != 'all':
            positions_df = positions_df[(positions_df['type'] == order_type_dict[order_type])]

        for i, position in positions_df.iterrows():
            order_result = close_position(position)

            print('order_result: ', order_result)


def check_allowed_trading_hours():
    if 9 < datetime.now().hour < 17:
        return True
    else:
        return False


def market_order(symbol, volume, order_type, deviation=20, magic=12345):

    order_type_dict = {
        'buy': mt5.ORDER_TYPE_BUY,
        'sell': mt5.ORDER_TYPE_SELL
    }

    price_dict = {
        'buy': mt5.symbol_info_tick(symbol).ask,
        'sell': mt5.symbol_info_tick(symbol).bid
    }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,  # FLOAT
        "type": order_type_dict[order_type],
        "price": price_dict[order_type],
        "sl": 0.0,  # FLOAT
        "tp": 0.0,  # FLOAT
        "deviation": deviation,  # INTERGER
        "magic": magic,  # INTERGER
        "comment": strategy_name,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    return(order_result)


if __name__ == '__main__':
    is_initialized = mt5.initialize()
    print('initialize: ', is_initialized)

    is_logged_in = mt5.login(LOGIN, PASSWORD, SERVER)
    print('logged in: ', is_logged_in)
    print('\n')

    while True:
        account_info = mt5.account_info()
        print(datetime.now(),
              '| Login: ', account_info.login,
              '| Balance: ', account_info.balance,
              '| Equity: ' , account_info.equity)

        num_positions = mt5.positions_total()

        if not check_allowed_trading_hours():
            close_positions('all')

        fast_sma = get_sma(symbol, timeframe, 10)
        slow_sma = get_sma(symbol, timeframe, 100)

        if fast_sma > slow_sma:
            close_positions('sell')

            if num_positions == 0 and check_allowed_trading_hours():
                order_result = market_order(symbol, volume, 'buy')
                print(order_result)

        elif fast_sma < slow_sma:
            close_positions('buy')

            if num_positions == 0 and check_allowed_trading_hours():
                order_result = market_order(symbol, volume, 'sell')
                print(order_result)

        time.sleep(1)




