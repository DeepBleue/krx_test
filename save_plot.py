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




def save_plot(code):
    name = stock.get_market_ticker_name(code)
    
    today = datetime.now().strftime("%Y%m%d")
    day_before = datetime.now() - timedelta(days=90)
    day_before = day_before.strftime("%Y-%m-%d")
    
    df = stock.get_market_ohlcv(day_before,today, code)
    
    condition = (df['시가'] == 0) & (df['고가'] == 0) & (df['저가'] == 0) & (df['종가'] != 0)
    df.loc[condition, ['시가', '고가', '저가']] = df.loc[condition, '종가']
    
    before_fourty_day_low = df.iloc[-40:-35]['저가'].min()
    before_fourty_day_low_idx = df.iloc[-40:-35]['저가'].idxmin()
    
    
    high_price = df.iloc[-20:-3]['고가'].max()
    high_price_idx = df.iloc[-20:-3]['고가'].idxmax()
    
    after_signal = df[df.index>high_price_idx]
    low_price = after_signal['저가'].min()
    low_price_idx = after_signal['저가'].idxmin()
    threshold_fluctuation = (high_price - low_price ) / low_price * 100 
    

    
    df.rename(columns={'시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume'}, inplace=True)
    df['Date'] = mdates.date2num(df.index.to_pydatetime())
    
    
    

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
    
    fig.add_trace(go.Scatter(x=[before_fourty_day_low_idx], y=[before_fourty_day_low],
                         mode='markers', marker=dict(color='blue', size=10),
                         showlegend=False),
              row=1, col=1)
    
    fig.add_trace(go.Scatter(x=[high_price_idx], y=[high_price],
                         mode='markers', marker=dict(color='red', size=10),
                         showlegend=False),
              row=1, col=1)
    
    percentage1 = (high_price-before_fourty_day_low)/before_fourty_day_low * 100
    percentage2 = (high_price-low_price)/low_price * 100
    
    fig.add_trace(go.Scatter(
        x=[before_fourty_day_low_idx],
        y=[(high_price+before_fourty_day_low)/2],
        error_y=dict(
        type='data', # value of error bar given in data coordinates
        array=[(high_price-before_fourty_day_low)/2],
        visible=True),
        text=[f'{percentage1:.2f}%'], 
        hoverinfo='text+x+y'
            ),
        row=1, col=1)
    fig.add_annotation(
        x=before_fourty_day_low_idx,
        y=high_price,
        text=f"{percentage1:.2f}%",
        showarrow=False,
        xshift=30
        # yshift=10  # Adjusts the position of the annotation
            )

    
    fig.add_trace(go.Scatter(
            x=[low_price_idx],
            y=[(high_price+low_price)/2],
            error_y=dict(
            type='data', # value of error bar given in data coordinates
            array=[(high_price-low_price)/2],
            visible=True),
            text=[f'{percentage2:.2f}%'], 
            hoverinfo='text+x+y'
                ),
            row=1, col=1)
    fig.add_annotation(
        x=low_price_idx,
        y=high_price,
        text=f"{percentage2:.2f}%",
        showarrow=False,
        xshift=30
        # yshift=10  # Adjusts the position of the annotation
            )
    
    
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
    # fig.show()
    fig.write_image(f"image/{name}.png")
    
    
if __name__ == '__main__':
    codes = ['011155', '001060', '009070', '092220', '058850', '229640', '017900', '083420', '004540', '004545', '003580', '000490', '012510', '286940', '204210', '068290', '009470', '145210', '112610', '047400', '011330', '084680', '007810', '020120', '011280', '091810', '001755', '180640', '004560', '011200', '054620', '211270', '083660', '241520', '900290', '028300', '060250', '104200', '222160', '218410', '035080', '242040', '212560', '950220', '033640', '234690', '348340', '064260', '006580', '299170', '317330', '206560', '005160', '088130', '418420', '294140', '281740', '090360', '108490', '277070', '377030', '100790', '418470', '323990', '438700', '337930', '064480', '365900', '251630', '146320', '014970', '042600', '294630', '063170', '140070', '067370', '036830', '253840', '298830', '099440', '276040', '025320', '013990', '099190', '084850', '027360', '131370', '140670', '900100', '174900', '255440', '270660', '246250', '088800', '205100', '356680', '236810', '058450', '291230', '198080', '156100', '073110', '143540', '368970', '138080', '065530', '082850', '043590', '299900', '179900', '351330', '450520', '100030', '049070', '175140', '254120', '289220', '159580', '079370', '144510', '358570', '051160', '284620', '032500', '102370', '009730', '166480', '950160', '448710', '365270', '405100', '355390', '091440', '246710', '356860', '440110', '388870', '150900', '189690', '220100', '321260', '053160', '300080', '032580', '147760', '041460', '066980', '076610', '220180', '065510']
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map(save_plot, codes)
    pool.close()
    pool.join()