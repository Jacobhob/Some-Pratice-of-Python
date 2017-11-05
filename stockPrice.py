import datetime as dt
import pandas as pd 
import pandas_datareader.data as web

# Set time period.
start = dt.datetime(2013, 1, 1)
end = dt.date.today()

# Achieve stock price from yahoo or google finance.
data_source = "yahoo" #"yahoo", "google"
stock = 'GOOGL' #Google
original_prices = web.DataReader(stock, data_source, start, end)
# Show original stock prices
#print(original_prices.head())

actions = web.DataReader(stock, "yahoo-actions", start, end)
# actions is a DataFrame variable, date with actions as index, contents are action and value
#print(actions.head())

dividends = web.DataaReader(stock, "yahoo-dividends", start, end)
# dividends is a DataFrame variable, index: date, contents: dividends 

# More: Financial quotes, Financial options...

# Merge two dataframes, date without actions will show "NaN" in action and vallue colume.
original_prices['actions'] = actions.action
original_prices['value'] = actions.value
#print(original_prices)

filename = "~/Documents/" + stock +".csv"
original_prices.to_csv(filename)