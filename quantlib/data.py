import pandas as pd
import yfinance as yf
import requests
import datetime
from bs4 import BeautifulSoup

def format_date(date):
    # convert 2012-02-06 00:00:00 >> datetime.date(2012, 2, 6)
    yymmdd = list(map(lambda x: int(x), str(date).split(" ")[0].split("-")))
    return datetime.date(yymmdd[0], yymmdd[1], yymmdd[2])

def get_sp500_instruments():
    res = requests.get(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            )
    soup = BeautifulSoup(res.content, 'lxml')
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))
    return list(df[0]["Symbol"])

def get_sp500_df():
    symbols = get_sp500_instruments()
    # to save time lets only grab 30 for now
    #symbols = symbols[:30]
    ohlcvs = {}
    for symbol in symbols:
        # Gives OHLCV + Dividend + Stock Splits
        symbol_df = yf.Ticker(symbol).history(period='10y')
        # print(symbol_df)
        # we are only interested in OHLCV, lets rename them
        ohlcvs[symbol] = symbol_df[
                ['Open', 'High', 'Low', 'Close', 'Volume']
            ].rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )
        print(symbol)
        print(ohlcvs[symbol])
    
    # now we want to put all that into a single Dataframe
    df = pd.DataFrame(index=ohlcvs["GOOGL"].index)
    df.index.name = "date"
    instruments = list(ohlcvs.keys())

    for inst in instruments:
        inst_df = ohlcvs[inst]
        # this transforms open, high... to AAPL open, AAPL high and so on
        columns = list(map(lambda x: "{} {}".format(inst, x), inst_df.columns))
        df[columns] = inst_df

    return df, instruments

def extend_dataframe(traded, df):
    df.index = pd.Series(df.index).apply(lambda x: format_date(x))
    open_cols = list(map(lambda x: str(x) + " open", traded))
    high_cols = list(map(lambda x: str(x) + " high", traded))
    low_cols = list(map(lambda x: str(x) + " low", traded))
    close_cols = list(map(lambda x: str(x) + " close", traded))
    volume_cols = list(map(lambda x: str(x) + " volume", traded))
    historical_data = df.copy()
    # get a df with ohlcv for all traded instruments
    historical_data = historical_data[open_cols + high_cols + low_cols + close_cols + volume_cols]
    # fill missing data first by forward filling data, such that [] [] [] a b c [] [] [] becomes [] [] [] a b c c c c
    historical_data.fillna(method="ffill", inplace=True)
    # fill missing data by backward filling data, such that [] [] [] a b c c c c becomes a a a a b c c c c
    historical_data.fillna(method="bfill", inplace=True)
    for inst in traded:
        # close to close return statistic
        historical_data["{} % ret".format(inst)] = historical_data["{} close".format(inst)] / historical_data["{} close".format(inst)].shift(1) -1
        # historical rolling standard deviation of returns as realised volatility proxy
        historical_data["{} % ret vol".format(inst)] = historical_data["{} % ret".format(inst)].rolling(25).std()
        # test if stock is actively trading by using rough measure of non-zero price change from previous time step
        historical_data["{} active".format(inst)] = historical_data["{} close".format(inst)] != historical_data["{} close".format(inst)].shift(1)
    return historical_data


"""
Note there are multiple ways to fill missing data, depending on you requirements and purpose
Some options
1. Ffill -> bfill
2. Brownian motion/bridge - simulating the dynamics of stock price
3. GARCH/GARCH Copula et cetera - used to model multivariate dependencies
4. Synthetic data, such as GAN and Stochastic Volatility Neural Networks

The choices differ for your requirments, for instance, in backtesting you might favour (1), while in training neural models you might favour (4)

Note that the data cycle can be very complicated, with entire reearch teamsdedicated to obtaining, processing and extracting signals from structure/unstructured data.
What we show today barely scratches the surface of the entire process, since we are dealing with well behaved data that is structued and already cleand for us by Yahoo Finance API
"""

