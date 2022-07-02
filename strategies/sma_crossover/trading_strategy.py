import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
from account_credentials import LOGIN, PASSWORD, SERVER

symbol = 'BTCUSD'
timeframe = mt5.TIMEFRAME_M5


def get_sma(symbol, timeframe, period):
    sma = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timeframe, 0, period))['close'].mean()

    return sma


def close_positions(order_type):
    order_type_dict = {
        'buy': 0,
        'sell': 1
    }

    if mt5.positions_total() > 0:
        positions = mt5.positions_get()

        positions_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())
        print(positions_df)

        positions_df = positions_df[(positions_df['type'] == order_type_dict[order_type])]
        print(positions_df)

        for i, row in positions_df.iterrows():
            order_result = mt5.Close(symbol, ticket=row['ticket'])
            print(order_result)


if __name__ == '__main__':
    is_initialized = mt5.initialize()
    print('initialize: ', is_initialized)

    is_logged_in = mt5.login(LOGIN, PASSWORD, SERVER)
    print('logged in: ', is_logged_in)
    print('\n')

    while True:
        num_positions = mt5.positions_total()
        print(num_positions)

        fast_sma = get_sma(symbol, timeframe, 10)
        slow_sma = get_sma(symbol, timeframe, 100)

        if fast_sma > slow_sma:
            close_positions('sell')

            if num_positions == 0:
                mt5.Buy('BTCUSD', 0.01)

        elif fast_sma < slow_sma:
            close_positions('buy')

            if num_positions == 0:
                mt5.Sell('BTCUSD', 0.01)

        time.sleep(1)




