import concurrent.futures
import pandas as pd
import yfinance as yf
import numpy as np
from tqdm import tqdm
from scipy.stats import linregress
from IPython.display import Image, display
from IPython.core.display import HTML
from finvizfinance.quote import finvizfinance
import matplotlib.pyplot as plt


def filter_stock():
    url = r'S:\stock screener project\screened_stock_v2.csv'
    ticker_df = pd.read_csv(url)
    ticker_list = ticker_df['Symbols'].tolist()

    return ticker_list

def cal_slope(arr):
    y = np.array(arr)
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return slope

def filter_by_vcp_conditions(df):
    moving_averages = [30, 50, 150, 200]
    for ma in moving_averages:
        df['SMA_' + str(ma)] = round(df['Close'].rolling(window=ma).mean(), 2)
    df['SMA_slope_30'] = df['SMA_30'].rolling(window = 20).apply(cal_slope)
    df['SMA_slope_200'] = df['SMA_200'].rolling(window = 20).apply(cal_slope)
    df['52_week_low'] = df['Close'].rolling(window = 5*52).min()
    df['52_week_high'] = df['Close'].rolling(window = 5*52).max()
    # latest_price = df['Close'][-1]

    # Condition 1: Price > 150 MA & 200 MA
    df['Condition1'] = (df['Close'] > df['SMA_150']) & (df['Close'] > df['SMA_200'])
    # Condition 2: 150 MA > 200 MA
    df['Condition2'] = (df['SMA_150'] > df['SMA_200'])
    # Condition 3: 30MA and 200 MA trending up for at least 1 month
    df['Condition3'] = (df['SMA_slope_30'] > 0.0) & (df['SMA_slope_200'] > 0.0)
    # Condition 4: 50 MA > 150 MA and 200 MA
    df['Condition4'] = (df['SMA_50'] > df['SMA_150']) & (df['SMA_150'] > df['SMA_200'])
    # Condition 5: Price > 50MA as the stock is coming out of a base (Not sure how to calculate base)
    df['Condition5'] = (df['Close'] > df['SMA_50'])
    # Condition 6: Price > 52-week low + 25%
    df['Condition6'] = (df['Close'] > df['52_week_low']* 1.25)
    # Condition 7: Price > 52-week high - 25%
    df['Condition7'] = (df['Close'] > df['52_week_high']* 0.75)
    # Condition 8: Pivot (5 day) Breakout
    winsize = 5
    df['Condition8'] = df['Close'] > ((df['Close']).rolling(window=winsize).mean()+ (df['Close']).rolling(window=winsize).max() + (df['Close']).rolling(window=winsize).min())/3
    # Condition 9: Contraction below 10%
    for handlesize in range(5, 41): # handlesize can be 5 days to 40 days (2 months)
        df[f'Condition9.{handlesize}'] = (( df['Close']).rolling(window=handlesize).max() - (df['Close']).rolling(window=handlesize).min()) / (df['Close']).rolling(window=handlesize).min() < 0.1

    df['Condition9'] = df[['Condition9.5','Condition9.6','Condition9.7','Condition9.8','Condition9.9','Condition9.10',
        'Condition9.11','Condition9.12','Condition9.13', 'Condition9.14','Condition9.15','Condition9.16',
        'Condition9.17','Condition9.18','Condition9.19', 'Condition9.20','Condition9.21','Condition9.22',
        'Condition9.23','Condition9.24','Condition9.25', 'Condition9.26','Condition9.27','Condition9.28',
        'Condition9.29','Condition9.30','Condition9.31', 'Condition9.32','Condition9.33','Condition9.34',
        'Condition9.35','Condition9.36','Condition9.37', 'Condition9.38','Condition9.39','Condition9.40'
        ]].any(axis='columns')

    df['Has_fulfilled'] = df[['Condition1','Condition2','Condition3','Condition4','Condition5','Condition6','Condition7','Condition8','Condition9']].all(axis='columns')

    return df[['Close','Has_fulfilled']]
    # return df

def scanning_wrapper(ticker_string):
    ticker = yf.Ticker(ticker_string)
    ticker_history = ticker.history(period = 'max')
    data = filter_by_vcp_conditions(ticker_history)
    df = pd.DataFrame()
    if data['Has_fulfilled'].tail(1).iloc[0] == True:
        print(ticker_string)
        #print(data)
        show_image(ticker_string)
        summarise = backtest(ticker_string, data)
        df[ticker_string] = summarise
        return df
    return df

def show_image(ticker):
    stock = finvizfinance(ticker)
    print(stock.ticker_charts())
    #display(Image(url=stock.ticker_charts()))

def backtest(ticker_string, df_i):
    df = pd.DataFrame()
    df['Has_fulfilled'] = df_i['Has_fulfilled']


    # Find the N days later price
    # Back test the profit/loss made if we sell after 120 days in recent year
    for i in range(1, 201):
        time = -i
        temp = pd.DataFrame()
        temp[f'Future_Close_{i}d'] = df_i['Close'].shift(periods = time)
        temp[f'Result_{i}d'] = ( temp[f'Future_Close_{i}d'] - df_i['Close']) / df_i['Close']
        df = pd.concat([df, temp[f'Result_{i}d']], axis=1)


    vcp_date = df[df['Has_fulfilled'] == True]
    vcp_date = vcp_date.drop(columns=['Has_fulfilled'], axis=1)
    #print(vcp_date)

    # Show the statistics data, focus on 'mean' which represent how much profit/loss
    # we make on average when selling the stock after N days
    summarise = vcp_date.mean()
    return summarise

def quick_scan(ticker_list):
    scan = pd.DataFrame()
    with concurrent.futures.ProcessPoolExecutor(max_workers = 1) as executor:
        data_list= list(tqdm(executor.map(scanning_wrapper, ticker_list), total=len(ticker_list)))
        scan = pd.concat(data_list, axis=1)
    return scan

def plot_graph(df):
    df['mean'] = df.mean(axis=1)
    df.plot(figsize=(10, 6),color='grey')
    df['mean'].plot(color='black',linewidth=2)
    plt.xlabel('Date')
    plt.ylabel('Pct Change')
    plt.title('Stock Prices Over holding days')
    plt.grid(True)


def main():
    ticker_list = filter_stock()
    #ticker_list = ['AXP','BOOT']
    df = quick_scan(ticker_list)
    plot_graph(df)
    df.to_csv('vcp_v1.csv', encoding='utf-8', index=False)


if __name__ == '__main__':
    main()
    scanning_wrapper('AIO')

