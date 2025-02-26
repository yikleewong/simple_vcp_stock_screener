There are two main functions for screening the stocks in NYSE : analysis.py and vcp_screener_stock.py
# VCP_Stock_Screener

## Analysis.py
### Data Crawling 
-Get tickers from 'NYSE' label using yfinance library (an open-sourced tool) and save it 
-fetch history price data and financial fundamental data, such as yearly or quarterly revenue, eps, gross profit, of tickers
*add time.sleep(1) to prevent numerous html requests to yahoo finance in short time

### Data Cleaning
-Correct symbol names with different special character '^', '/', it should be '.' mostly
-Remove symbols that are delisted from NYSE already

### Data Analysis
-Use linear Regression Model to calculate the slope of price movement last three months
-Calculate the mean of history price as moving average as another proof of uptrending
-Calculate the percentage change of revenue, gross profit and eps growth yearly or quarterly as simple fundamental analysis
-Count the number of True value returned as multi-layers to screen stocks instead of filtering under various conditions

## vcp_stock_screener.py
### Data processing
-Use the outputed .csv from analysis.py and filter out unavaliable symbols with count = 0 and 1

### Data analysis
-Apply the nine vcp condintions defined by Mark Minervini
-show stock price graph from fivizfinance 
-Apply backtest to see the price change within 200days whenever the vcp screener = True
-Calculate the mean of percentages price changesd within 200days among all stocks that met requirements
-Plot graph 
![holdingDays](https://github.com/user-attachments/assets/cf98f89c-b33f-4486-b4fe-2e39c5dad748)
X-axis represents the period you hold the stock whenever vcp signal is True
Y-axis represents the mean percentage changed 

## Conclusion
This figure shows a uptrend through the time period, the longer you hold a stock.
VCP signal applys to most of the stocks, however, the signal appears too often making the pct change is mainly in range of 0-0.5%


