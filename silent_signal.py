from pykrx import stock
from datetime import timedelta
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots







if __name__ == '__main__':
    
    
    
    KOSPI = stock.get_market_ticker_list("20190225", market="KOSPI")
    KOSDAQ = stock.get_market_ticker_list("20190225", market="KOSDAQ")
    code = KOSDAQ[100]
    code = '121890'
    name = stock.get_market_ticker_name(code)

    
    
    time_delta =  timedelta(days=40)
    
    today = datetime.now() - time_delta
    today = today.strftime("%Y%m%d")  
    day_before = datetime.now() - timedelta(days=90) - time_delta
    day_before = day_before.strftime("%Y-%m-%d")
    
    
    df = stock.get_market_ohlcv(day_before,today, code)
    
    condition = (df['시가'] == 0) & (df['고가'] == 0) & (df['저가'] == 0) & (df['종가'] != 0)
    df.loc[condition, ['시가', '고가', '저가']] = df.loc[condition, '종가']
    
    print(len(df))
    
    ############### 40일전 저거 대비 현재 등락률 
    before_fourty_day_low = df.iloc[-40]['저가']
    before_fourty_day = df.iloc[-40].index
    today_close = df.iloc[-1]['종가']
    fluctuation = (today_close - before_fourty_day_low) / before_fourty_day_low * 100 



    
    if fluctuation > 90 : 
        print('등락률이 90%가 넘습니다.')   
        
    else : 
        print('등락률이 낮습니다.')
        print(f'fluc : {fluctuation:.2f}%')
        
        
        
    ############### 15일 전 ~ 5일전 고가 대비 최근 저가
    high_price = df.iloc[-15:-5]['고가'].max()
    high_price_idx = df.iloc[-15:-5]['고가'].idxmax()
    
    after_signal = df[df.index>high_price_idx]
    low_price = after_signal['저가'].min()
    low_price_idx = after_signal['저가'].idxmin()
    threshold_fluctuation = (high_price - low_price ) / low_price * 100 
    
    
    if threshold_fluctuation < 20 : 
        print('flat base가 20%를 넘지 않습니다.')
        print(f'flat base : {threshold_fluctuation:.2f}%')
        
    else : 
        print('flat base가 20%를 넘어갑니다.')
        print(f'flat base : {threshold_fluctuation:.2f}%')
    
    
    ###############  고가와 현재가 비교
    current_price = df.iloc[-1]['종가']
    temp_fluc = (current_price - high_price) / high_price * 100
    if high_price > current_price: 
        print('현재가가 고가를 넘지 않습니다.')
        print(f'fluc : {temp_fluc:2f}%')
        
    else : 
        print('현재가가 고가를 넘었습니다.')
        print(f'fluc : {temp_fluc:2f}%')
        
        

    
    ####### Show the plot         
        
    df.rename(columns={'시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume'}, inplace=True)
    df['Date'] = mdates.date2num(df.index.to_pydatetime())
    
    
    
    ohlc_data = df[['Date', 'Open', 'High', 'Low', 'Close']].values
    volume_data = df['Volume']
        
    

    # Create a figure with subplots: 2 rows, 1 column
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, 
                        row_heights=[0.6,0.2,0.2])

    # Add the candlestick plot in the first (top) subplot
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close']),
                row=1, col=1)
    
    fig.add_trace(go.Scatter(x=[df.index[-40]], y=[df.iloc[-40]['Low']],
                         mode='markers', marker=dict(color='blue', size=10),
                         showlegend=False),
              row=1, col=1)
    
    fig.add_trace(go.Scatter(x=[high_price_idx], y=[high_price],
                         mode='markers', marker=dict(color='red', size=10),
                         showlegend=False),
              row=1, col=1)
    percentage = (high_price-low_price)/low_price * 100
    fig.add_trace(go.Scatter(
            x=[low_price_idx],
            y=[(high_price+low_price)/2],
            error_y=dict(
            type='data', # value of error bar given in data coordinates
            array=[(high_price-low_price)/2],
            visible=True),
            text=[f'{percentage:.2f}%'], 
            hoverinfo='text+x+y'
                ),
            row=1, col=1)
    

    # Add the volume bar chart in the second (bottom) subplot
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color='blue'),
                row=3, col=1)
    


    # Update layout of the figure
    fig.update_layout(
        title=name,
        xaxis_title='High Tight Flag',
        yaxis_title='가격',
        yaxis2_title='거래량',
        xaxis2_rangeslider_visible=False,
        showlegend=False,
        height=800
    )

    # Update axis labels for each subplot
    fig.update_xaxes(title_text="date", row=3, col=1)
    fig.update_yaxes(title_text="price", row=1, col=1)
    fig.update_yaxes(title_text="volume", row=2, col=1)
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]), #hide weekends
            # dict(values=["2023-12-25", "2024-01-01"])  # hide Christmas and New Year's
        ]
    )
    fig.show()
    # fig.write_image(f"image/{code}.png")
