from pykrx import stock
from datetime import timedelta,datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import multiprocessing
import numpy as np
import json

def save_dict(code,code_dict):
    today = datetime.now().strftime("%Y%m%d")  
    with open(f'log/{today}_log.txt', 'a') as file:
        for key, value in code_dict.items():
            file.write(f'{key}: {value}\n')


def analyze_stock(code):
    done = False
    name = stock.get_market_ticker_name(code)
    
    code_log = {}
    
    # time_delta =  timedelta(days=0)
    
    today = datetime.now() 
    today = today.strftime("%Y%m%d")  
    day_before = datetime.now() - timedelta(days=90)
    day_before = day_before.strftime("%Y-%m-%d")
    
    sample_df = stock.get_market_ohlcv(day_before,today, '005930')
    
    df = stock.get_market_ohlcv(day_before,today, code)
    
    condition = (df['시가'] == 0) & (df['고가'] == 0) & (df['저가'] == 0) & (df['종가'] != 0)
    df.loc[condition, ['시가', '고가', '저가']] = df.loc[condition, '종가']

    
    
    if len(df) != len(sample_df) : 
        code_log[code] = 'df len problem'
        save_dict(code,code_log)
        return done,code
    else :
        pass
    
    if '스팩' in name : 
        code_log[code] = 'spac stock'
        save_dict(code,code_log)
        return done , code
    else : 
        pass
    
    

    has_nan = df.isna().any().any()
    has_inf = np.isinf(df).any().any()

    if has_nan or  has_inf: 
        code_log[code] = 'has nan or inf'
        save_dict(code,code_log)
        return done , code
    else : 
        pass
    
    
    current_close_price = df.iloc[-1]['종가']
    
    if current_close_price > 100000 or current_close_price < 1000:
        code_log[code] = 'high or low price'
        save_dict(code,code_log)
        return done, code 
    else : 
        pass
    
    ############### 40일전 저거 대비 현재 등락률 
    before_fourty_day_low = df.iloc[-40:-35]['저가'].min()
    before_fourty_day = df.iloc[-40:-35]['저가'].idxmin()
    high_price = df.iloc[-20:-3]['고가'].max()
    today_close = df.iloc[-1]['종가']
    
    if before_fourty_day_low == 0 : 
        code_log[code] = 'have zero value'
        save_dict(code,code_log)
        return done, code
    else : 
        pass
    
    fluctuation = (high_price - before_fourty_day_low) / before_fourty_day_low * 100 



    
    if fluctuation > 35 : 
        pass
        
    else : 
        code_log[code] = 'fluctuation under 35%'
        save_dict(code,code_log)
        return done ,code 

        
    ############### 15일 전 ~ 6일전 고가 대비 최근 저가
    high_price = df.iloc[-20:-3]['고가'].max()
    high_price_idx = df.iloc[-20:-3]['고가'].idxmax()
    close_price_before = df.loc[high_price_idx, '종가']

    
    after_signal = df[df.index>high_price_idx]
    low_price = after_signal['저가'].min()
    low_price_idx = after_signal['저가'].idxmin()
    
    mid_price = (high_price+ close_price_before)/2
    
    
    if low_price == 0 : 
        code_log[code] = 'have zero value'
        save_dict(code,code_log)
        return done, code 
    else : 
        pass
    
    threshold_fluctuation = (high_price - low_price ) / low_price * 100 
    
    
    if threshold_fluctuation < 30 : 
        code_log[code] = 'high flat base'
        save_dict(code,code_log)
        pass
        
    else : 
        return done , code 
    
    
    ###############  고가와 현재가 비교
    current_price = df.iloc[-1]['종가']
    
    if high_price == 0 : 
        code_log[code] = 'have zero value'
        save_dict(code,code_log)
        return done, code 
    else : 
        pass
    
    temp_fluc = (current_price - high_price) / high_price * 100
    if high_price > current_price: 
        pass
        
    else : 
        code_log[code] = 'high current price'
        save_dict(code,code_log)
        return done, code
    
    
    done = True 
    return done , code 
        

if __name__ == '__main__':
    
    signal_code = []

    today = datetime.now().strftime("%Y%m%d")
    KOSDAQ = stock.get_market_ticker_list(today, market="KOSDAQ")
    KOSPI = stock.get_market_ticker_list("20190225", market="KOSPI")
    
    MARKET = KOSPI + KOSDAQ
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    results = pool.map(analyze_stock, MARKET)
    pool.close()
    pool.join()

    # Process the results
    for result in results:
        done, code = result
        
        if done :
            signal_code.append(code)
            
    
    print(signal_code)
        
        
    
    