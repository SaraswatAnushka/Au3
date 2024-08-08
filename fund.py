# from bs4 import BeautifulSoup
# import requests
import pandas as pd
import numpy as np
from flask import Flask, request, render_template

app = Flask("__name__")

q=""

@app.route("/")
def loadPage():
	return render_template('index.html', query="")


def create_data_frame(no_of_months,no_of_year):
    Composite_bond_index = {
        '1month' : -0.01,
        '3month' : 2.42,
        '12month' : 8.46,
        '3year' : 4.75,
        '5year' : 7.73
    }

    Hybrid_35_65 = {
        '1month' : 2.61,
        '3month' : 8.96,
        '12month' : 18.06,
        '3year' : 18.13,
        '5year' : 12.29
    }

    Nifty = {
        '1month' : -1.06,
        '3month' : 7.24,
        '12month' : 9.75,
        '3year' : 48.21,
        '5year' : 119.82
    }

    Gold_ETF = {
        '1month' : -4.26,
        '3month' : -2.50,
        '12month' : 15.76,
        '3year' : 12.08,
        '5year' : 12.47
    }

    composite_bond_df = pd.DataFrame(Composite_bond_index,index=[0])
    hybrid_35_fund  = pd.DataFrame(Hybrid_35_65,index=[0])
    Nifty_fund = pd.DataFrame(Nifty,index=[0])
    Gold_ETF_fund = pd.DataFrame(Gold_ETF,index = [0])

    if(no_of_months!=0):
        datas = {
            'fund1': composite_bond_df['{}'.format(no_of_months)+'month'],
            'fund2': hybrid_35_fund['{}'.format(no_of_months)+'month'],
            'fund3': Nifty_fund['{}'.format(no_of_months)+'month'],
            'fund4': Gold_ETF_fund['{}'.format(no_of_months)+'month']
        }
    elif(no_of_year!=0):
        datas = {
            'fund1': composite_bond_df['{}'.format(no_of_year)+'year'],
            'fund2': hybrid_35_fund['{}'.format(no_of_year)+'year'],
            'fund3': Nifty_fund['{}'.format(no_of_year)+'year'],
            'fund4': Gold_ETF_fund['{}'.format(no_of_year)+'year']
        }
    dataFrame = pd.DataFrame(datas)
    return dataFrame



@app.route("/", methods=['POST'])


def predict():
    n=0
    m=0
    time = request.form['time']
    risk = request.form['risk']

    if time=='1 month':
         n=1
    elif time =='3 month':
         n=3
    elif time =='12 month':
         n=12
    
    if time =='3 year':
         m=3
    elif time=='5 year':
         m=5

    data = create_data_frame(n,m)

    random_weights = np.array(np.random.random(4))
    rebalance_weights = random_weights/(np.sum(random_weights))
    exp_return = np.sum(( data* rebalance_weights).values)
    exp_volatility = np.sqrt(np.dot(rebalance_weights.T, np.dot(np.cov(data,ddof = 0),rebalance_weights)))

    sharpe_ratio = (exp_return - .07)/exp_volatility

    number_of_symbols = 4

    num_of_portfolio = 5000

    all_weights = np.zeros((num_of_portfolio, number_of_symbols))
    ret_arr = np.zeros(num_of_portfolio)
    vol_arr = np.zeros(num_of_portfolio)
    sharpe_arr = np.zeros(num_of_portfolio)

    #Start the simulation

    for ind in range(num_of_portfolio):
        weights = np.array(np.random.random(number_of_symbols))
        weights = weights/np.sum(weights)
        all_weights[ind,:] = weights
        ret_arr[ind] = np.sum((data * weights).values)
        vol_arr[ind] = np.sqrt(
            np.dot(weights.T, np.dot(np.cov(data,ddof=0), weights))
        )
        sharpe_arr[ind] = (ret_arr[ind]-0.07)/vol_arr[ind]

    simulations_data = [ret_arr,vol_arr, sharpe_arr, all_weights]
    simulation_df = pd.DataFrame(data = simulations_data).T

    # Add the column names
    simulation_df.columns = [
        'Returns',
        'Volatility',
        'Sharpe Ratio',
        'Portfolio Weights'
    ]

    # Make sure the data types are correct, we don't want our floats to be strings.
    simulation_df = simulation_df.infer_objects()

    # Print out the results.
    # print('')
    # print('='*80)
    # print('SIMULATIONS RESULT:')
    # print('-'*80)
    # print(simulation_df.head())
    # print('-'*80)
    max_return = simulation_df['Returns'].max()
    max_return_index = simulation_df['Returns'].idxmax()
    max_return_row = simulation_df.loc[max_return_index]
    

    o1= 'return: {returns} risk : {risk} '.format(returns = max_return_row['Returns'], risk = max_return_row['Volatility'])

    return render_template('index.html',output1=o1)

app.run(debug=True,port=5002)