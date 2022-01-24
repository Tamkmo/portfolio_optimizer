import os
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from MCForecastTools import MCSimulation
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objs as go
import flask
import numpy as np
import random
from dash.dependencies import Input, Output
load_dotenv()
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
type(alpaca_api_key)
type(alpaca_secret_key)
alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version="v2")
tickers = ["AGG", "SPY", "VTV"]
start_date = pd.Timestamp("2018-12-31", tz="America/New_York").isoformat()
end_date = pd.Timestamp("2021-12-31", tz="America/New_York").isoformat()
timeframe = "1D"
limit_rows = 1000
prices_df = alpaca.get_barset(
    tickers,
    timeframe,
    start=start_date,
    end=end_date,
    limit=limit_rows
).df
prices_df.head()
MC_even_weight = MCSimulation(
    portfolio_data = prices_df,
    weights = [.33,.33,.33],
    num_simulation = 100,
    num_trading_days = 252*5
)
MC_even_weight.portfolio_data.head()
MC_even_weight.calc_cumulative_return()
sim_df = MC_even_weight.calc_cumulative_return()
shift_df = sim_df.shift(-1)
returns_df = (shift_df - sim_df) / sim_df
returns_df
annual_std_list = returns_df.std() * (252 **0.5)
annual_std_list
annual_std = annual_std_list.mean()
annual_std
annual_ret_list = returns_df.mean() * 252
annual_ret_list
annual_ret = annual_ret_list.mean()
annual_ret
annual_income = .02
def simulate_return(mean_return, standard_dev, annual_income, simulated_quarters, number_of_simulations, initial_investment):
    quarterly_ret = (mean_return/4) + (annual_income/4)
    quarterly_stdev = standard_dev / (4**0.5)
    quarterly_returns = 1 + np.random.normal(quarterly_ret, quarterly_stdev, (simulated_quarters,number_of_simulations))
    portfolio = np.zeros_like(quarterly_returns)
    portfolio[0] = initial_investment
    for t in range (1, simulated_quarters):
        portfolio[t] = (portfolio[t-1]*quarterly_returns[t])
    return pd.DataFrame(portfolio)
simulate_return(annual_ret,annual_std,annual_income,20,100,1).plot(figsize = (20,12), legend=None)
simulate_return(annual_ret,annual_std,annual_income,20,100,1).tail(1).mean(axis=1)

from app import app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__) # define flask app.server

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server) # call flask server

df = pd.DataFrame(simulate_return(annual_ret,annual_std,annual_income,20,100,1))
df.reset_index(inplace=True)
df1 = df.rename(columns = {'index':'quarters'})
df2 = pd.melt(df1, id_vars='quarters', value_vars=df1.columns[:-1])
fig = px.line(df2, x="quarters", y="value", color ="variable")

app.layout = html.Div(children=[
    html.H1(children='Monte Carlo simulations', 
            style={'textAlign': 'center'}), 
        #html.Div(html.Ul(id='tickers',
            #children=[html.Li(i) for i in tickers],
            #style={'textAlign': 'center'})), 
        dcc.Graph(
            id='Monte Carlo simulations',
            figure=fig),
        html.Label('multi-dropdown'),
        dcc.Dropdown(
            options=[
                {'label': 'DIA', 'value': 'ticker1'},
                {'label': 'QQQ', 'value': 'ticker2'},
                {'label': 'SPY', 'value': 'ticker3'},
                {'label': 'DVY', 'value': 'ticker4'},
                {'label': 'VBK', 'value': 'ticker5'},
                {'label': 'VXF', 'value': 'ticker6'},
                {'label': 'VNQ', 'value': 'ticker7'},
                {'label': 'ARKK', 'value': 'ticker8'},
                {'label': 'IWM', 'value': 'ticker9'},
                {'label': 'LQD', 'value': 'ticker10'},
                {'label': 'IEI', 'value': 'ticker11'},
                {'label': 'AGG', 'value': 'ticker12'}
            ],
            value=['ticker1', 'ticker2', 'ticker3'],
            multi=True
        ),
])



#app.callback(
    #[dash.dependencies.Output('totalsales', 'figure'), dash.dependencies.Output('Text', 'children')],
    #[dash.dependencies.Input('ticker1', 'value'),
    # dash.dependencies.Input('ticker2', 'value')
    # dash.dependencies.Input('ticker3', 'value')
    # dash.dependencies.Input('allocation1', 'end_date')
    # dash.dependencies.Input('allocation2', 'end_date')
    # dash.dependencies.Input('allocation3', 'end_date')])

#def update_graph(ticker1, ticker2, ticker3, allocation1, allocation2, allocation3):

    #tickers = (ticker1, ticker2, ticker3)
    #start_date = pd.Timestamp("2018-12-31", tz="America/New_York").isoformat()
    #end_date = pd.Timestamp("2021-12-31", tz="America/New_York").isoformat()
    #timeframe = "1D"
    #limit_rows = 1000
    #prices_df = alpaca.get_barset(
        #tickers,
        #timeframe,
        #start=start_date,
        #end=end_date,
        #limit=limit_rows
    #).df
    #MC_weight = MCSimulation(
    #portfolio_data = prices_df,
    #weights = [allocation1, allocation2, allocation3],
    #num_simulation = 100,
    #num_trading_days = 252*5
    #)
    #MC_weight.calc_cumulative_return()
    #MC_sim_line_plot = MC_weight.plot_simulation()




if __name__ == '__main__':
    app.run_server(debug=True)



