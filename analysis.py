import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import time

def calculate_revenue_growth(ticker):
    stock = yf.Ticker(ticker)

    # Calculate Yearly Revenue Growth
    financials = stock.financials
    if financials.empty:
        return 'cant_fetch'
    try:
        revenue = financials.loc['Total Revenue']
    except KeyError:
        return 'no data'
    if len(revenue) <= 1 or (revenue == 0).any():
        return 'insufficient'
    yearly_growth = revenue.pct_change(-1,fill_method=None).dropna() * 100

    if len(yearly_growth) >= 2 and all(yearly_growth[:3] > 20 ):
        return 'True'

    return 'False'

def calculate_EPS_growth(ticker):
    stock = yf.Ticker(ticker)

    # Calculate Quarterly EPS Growth
    quarterly_financials = stock.quarterly_financials
    if quarterly_financials.empty:
        return 'cant_fetch'
    try:
        eps = quarterly_financials.loc['Basic EPS']
    except KeyError:
        return 'no data'
    if len(eps) <= 1 or (eps == 0).any():
        return 'insufficient'
    quarterly_growth = eps.pct_change(-1,fill_method=None).dropna() * 100

    if len(quarterly_growth) >= 2 and all(quarterly_growth[:3] > 20 ):
        return 'True'

    return 'False'

def calculate_gross_profit_growth(ticker):
    stock = yf.Ticker(ticker)
    gp_yearly = 'False'
    gp_quarterly = 'False'

    # Calculate Quarterly Gross Profit Growth
    quarterly_financials = stock.quarterly_financials
    if quarterly_financials.empty:
        gp_quarterly = 'q_empty'
    if 'Gross Profit' in quarterly_financials.index:
        quarterly_gross_profit = quarterly_financials.loc['Gross Profit']
        if len(quarterly_gross_profit) <= 1 or (quarterly_gross_profit == 0).any():
            gp_quarterly = 'q_insuffidata'
        else:
            quarterly_growth = quarterly_gross_profit.pct_change(-1,fill_method=None).dropna() * 100
            if len(quarterly_growth) >= 2 and all(quarterly_growth[:3] > 20 ):
                gp_quarterly = 'True'
    else:
        gp_quarterly = 'q_no_gp'


    # Calculate Yearly Gross Profit Growth
    financials = stock.financials
    if financials.empty:
        gp_yearly = 'y_empty'
    else:
        if 'Gross Profit' in financials.index:
            gross_profit = financials.loc['Gross Profit']
            if len(gross_profit) <= 1 or (gross_profit == 0).any():
                gp_yearly = 'y_insuffidata'
            else:
                yearly_growth = gross_profit.pct_change(-1,fill_method=None).dropna() * 100
                if len(yearly_growth) >= 2 and all(yearly_growth[:3] > 20 ):
                    gp_yearly = 'True'
        else:
            gp_yearly = 'y_no_gp'



    return gp_yearly, gp_quarterly

def calculate_moving_averages(ticker):
    stock = yf.Ticker(ticker)
    try:
        price = stock.info['previousClose']
    except:
        return 0, 'cant_fetch'
    # Get historical market data
    historical_data = stock.history(period="ytd")
    if historical_data.empty:
        return price, 'cant_fetch_history'
    # Calculate 150-day and 200-day moving averages
    historical_data['150_MA'] = historical_data['Close'].rolling(window=150).mean()
    historical_data['200_MA'] = historical_data['Close'].rolling(window=200).mean()

    if historical_data['150_MA'].empty or historical_data['200_MA'].empty:
        return price, 'insufficient'
    # Get the last available moving average values
    ma_150 = historical_data['150_MA'].iloc[-1]
    ma_200 = historical_data['200_MA'].iloc[-1]
    if price > ma_200 and ma_150 > ma_200:
        return price, 'True'
    else:
        return price, 'False'


def is_uptrending(ticker):
    stock = yf.Ticker(ticker)
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')

    # Fetch historical market data for the past 3 months (90 days)
    historical_data = stock.history(start=start_date, end=end_date)
    # Ensure there is sufficient data
    if historical_data.shape[0] < 2:
        return False, "Insufficient data"
    # Extract closing prices and convert dates to numerical format
    closing_prices = historical_data['Close']
    dates = np.array([i for i in range(len(closing_prices))]).reshape(-1, 1)

    # Perform linear regression
    model = LinearRegression()
    model.fit(dates, closing_prices)
    slope = model.coef_[0]
    if slope > 0:
        return 'True'

    return 'False'

def get_nyse_tickers():
    url = r'S:\stock screener project\nasdaq_screener_1734771000122.csv'
    nyse_df = pd.read_csv(url)
    # Filter the DataFrame for NYSE tickers
    nyse_tickers = nyse_df['Symbol'].tolist()

    return nyse_tickers

def screen_stock():
    screened_stock = []
    nyse_tickers = get_nyse_tickers()

    for ticker in nyse_tickers:
        temp = []
        print(f"processing {ticker}")
        uptrend = is_uptrending(ticker)
        price, stage2 = calculate_moving_averages(ticker)
        gp_yearly, gp_quarterly = calculate_gross_profit_growth(ticker)
        revenue = calculate_revenue_growth(ticker)
        eps = calculate_EPS_growth(ticker)
        temp = [ticker, price, uptrend, stage2, gp_yearly, gp_quarterly, revenue, eps]
        count = temp.count('True')
        temp.append(count)
        screened_stock.append(temp)
        time.sleep(1)

    return screened_stock

def main():
    screened_stock = screen_stock()
    df = pd.DataFrame(screened_stock, columns=['Symbols', 'Price', 'IsUptrend', 'AboveMA', 'Yearly_Profit_20%', 'Quarterly_Profit_Growth', 'Revenue_Growth', 'EPS_Growth', 'Symptoms_Count'])
    df.to_csv('screened_stock_v1.csv', encoding='utf-8', index=False)
    print("generated file for analysis")

if __namne__ == '__main__':
    main()
