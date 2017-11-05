import numpy as np
import pandas as pd 
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import scipy.optimize as solver
import datetime as dt 
from functools import reduce

# A basket of stocks
tickers = ["AAPL", "FB", "GOOG", "MSFT"]
q = len(tickers)

# Set time period and datasource
start = dt.datetime(2010, 1, 1)
end = dt.date.today()
datasource = "yahoo"
database = pd.DataFrame()

# Store adjusted close price of each stock to a dataframe.
get_record = 0 # In order to make sure every stock has record in certain period.
for i in tickers:
	tmp = web.DataReader(i, datasource, start, end)
	database[i] = tmp['Adj Close']
	if get_record == 0:
		get_record = len(tmp)
	else: 
		get_record = min(get_record, len(tmp))

# Assumption: Use log to calculate return.
returns = np.log(database / database.shift(1)) # DataFrame.shift(1) means shift all the data downwards 1 row.
returns = returns.tail(get_record - 1) # DataFrame.tail() returns the last n rows
returns.fillna(value = 0, inplace = True) # Replace NaN and not change the original dataframe.

# Get mean and cov mtrix.
mean = returns.mean() * 252
cov = returns.cov() * 252
print(mean)
print(cov)

''' Comments:
returns这个DataFrame有很多缺陷，比如有些日子有些证券停牌了，没有发布股价，
因此当天的return是NaN，再比如说Facebook在2010年还没有上市，那段时间的股价和收益率也是NaN，
因此，我们要剪除未上市的记录，并将上市后停牌的日期的收益率填补为0， 
为了实现这两个目的，我们用到了DataFrame的两个Attribute，一个是.tail(), 
它的功能是返回DataFrame最后的指定条数的数据；另一个是.fillna()，
它的作用是为了填补该DataFrame中的NaN，将其填补为我们需要的值，并返回新的DataFrame.
'''

# Assign value to a weight numpy array.

while True:
	weight_array = []
	for count in range(q):
		instruction = "Please input a weight for stock " + tickers[count] + ": "
		tmpfloat = float(input(instruction))
		weight_array.append(tmpfloat)
	w = np.array(weight_array)
	if w.sum() == 1:
		break

#print(w)

# Matrix multiplication to calculate portfolio return and portfolio SD.
def sd(w):
	return np.sqrt(reduce(np.dot, [w,cov, w.T]))

portfolio_return = sum(w * mean)
portfolio_standard_deviation = sd(w)

# Set up diagram.
def diagram_setup(tickers):
	plt.grid(True)
	title = "Efficient Frontier : "
	for stock in tickers:
		title = title + stock + ' '
	plt.title(title)
	plt.xlabel('portfolio volatility')
	plt.ylabel('portfolio return')

# Ploting Markowitz efficient frontier.
sds = []
rtn = []
for _ in range(100000):
    w = np.random.rand(q)
    w /= sum(w)
    rtn.append(sum(mean * w))
    sds.append(np.sqrt(reduce(np.dot, [w, cov, w.T])))

diagram_setup(tickers)
plt.show(plt.plot(sds, rtn, 'ro')) # ro for red dot


# Use solver.minimize to solve for frontier
expected_return = np.arange(.10, .40, .005) # Start from 10%, end up in 40%, step 0.5%
risk = []

x0 = np.array([1.0 / q for x in range(q)])
bounds = tuple((0,1) for x in range(q))

for i in expected_return:
	constraints = [{'type': 'eq', 'fun': lambda x: sum(x) - 1}, {'type': 'eq', 'fun': lambda x: sum(x * mean) - i}]
	outcome = solver.minimize(sd, x0 = x0, constraints = constraints, bounds = bounds)
	#print(outcome)
	risk.append(outcome.fun)
diagram_setup(tickers)
plt.show(plt.plot(risk, expected_return, 'x'))
s
# Find minimum standard deviation
constraints = {'type': 'eq', 'fun': lambda x: sum(x) - 1}
minv = solver.minimize(sd, x0=x0, constraints=constraints, bounds=bounds).fun
minvr = sum(solver.minimize(sd, x0=x0, constraints=constraints, bounds=bounds).x * mean)

diagram_setup(tickers)
plt.show(plt.plot(minv, minvr, 'g*')) # w* for white star
