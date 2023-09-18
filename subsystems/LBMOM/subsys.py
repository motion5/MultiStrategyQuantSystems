import json
import quantlib.indicators_cal as indicators_cal
from pathlib import Path
import quantlib.backtest_utils as backtest_utils
import pandas as pd
import numpy as np


class Libmom:
    def __init__(self, instruments_config, historical_df, simulation_start, vol_target):
        self.pairs = [
            (28, 65),
            (143, 218),
            (135, 226),
            (144, 222),
            (191, 276),
            (71, 80),
            (29, 98),
            (32, 175),
            (39, 105),
        ]
        self.instruments_config = instruments_config
        self.historical_df = historical_df
        self.simulation_start = simulation_start
        self.vol_target = vol_target
        with open(instruments_config) as f:
            self.instruments_config = json.load(f)
        self.sysname = "LBMOM"

    """ 
    Implementing the strategy API - this is what the class promises to 
    provide to the rest of the library (it's an interface)
    1. Function to get the indicators for a specific strategy
    2. Function to run backtests and get positions
    """

    def extend_historicals(self, instruments, historical_data):
        # We need to obtain data with regards to the LBMOM strategy
        # in particular, we want the moving averages, which is a proxy
        # for momentum factor
        # We also want a univariate statistical factor as an indicator of regime.
        # We use the average directional index ADX as a proxy for momentum
        # regime indicator
        for inst in instruments:
            historical_data["{} adx".format(inst)] = indicators_cal.adx_series(
                high=historical_data["{} high".format(inst)],
                low=historical_data["{} low".format(inst)],
                close=historical_data["{} close".format(inst)],
                n=14,
            )
            for pair in self.pairs:
                # calculate the fastMA - slowMA
                historical_data[
                    "{} ema{}".format(inst, str(pair))
                ] = indicators_cal.ema_series(
                    historical_data["{} close".format(inst)], n=pair[0]
                ) - indicators_cal.ema_series(
                    historical_data["{} close".format(inst)], n=pair[1]
                )
        # the historical_data has all the information required for backtesting
        return historical_data

    def run_simulation(self, historical_data):
        """
        Init Params
        """
        instruments = self.instruments_config["instruments"]

        """
        Pre-processing
        """
        historical_data = self.extend_historicals(
            instruments=instruments, historical_data=historical_data
        )
        # print(historical_data)
        portfolio_df = pd.DataFrame(
            index=historical_data[self.simulation_start :].index
        ).reset_index()
        portfolio_df.loc[0, "capital"] = 10000
        is_halted = (
            lambda inst, date: not np.isnan(
                historical_data.loc[date, "{} active".format(inst)]
            )
            and (-historical_data[:date].tail(3)["{} active".format(inst)]).any()
        )
        # print(portfolio_df)

        """
        Run Simulation
        We are going to be using Asset management techniques called 
        'Volatility Targeting' - at both the asset level and the strategy level

        I've added notes to Obsidian for the intros to each of those articles
        and further reading which is useful, since HangukQuant doesn't make
        those articles avialable on his substack anymore

        We will also be using voting systems to account for the degree of expected
        returns. In particular, if there are more moving averages that indicate 
        momentum, then we want to bet bigger (use more risk)

        In general this means that we lever our capital to obtain a certain target 
        annualized level of volatilit, which is our proxy for risk/exposure. 
        This is controlled by the parameter VOL_TARGET, tat we pass from the 
        main driver.

        The relative allocations in a vol target framework is that positions are 
        inversley proportional to their volatility. In other words, a priori we assign 
        the same risk to each position, when not taking into account the relative
        alpha (momentum) strengths.

        So we assume 3 different risk/captial allocation techniques
        1. Strategy Vol targeting (veritical across time)
        2. Asset Vol Targeting (relative across assets)
        3. Voting Systems (Indicating the degree of momentum factor)
        """
        for i in portfolio_df.index:
            date = portfolio_df.loc[i, "date"]
            """
            Asset Scalar: What is the relative risk of the asset 
            compared to other assets at a certain time instance
            """
            strat_scalar = 2  # strategy scalar (refer to post)
            tradeable = [inst for inst in instruments if not is_halted(inst, date)]
            non_tradeable = [inst for inst in instruments if inst not in tradeable]

            """
            Get PnL, Scalars
            """
            if i != 0:
                date_prev = portfolio_df.loc[i - 1, "date"]
                pnl, nominal_ret = backtest_utils.get_backtest_day_stats(
                    portfolio_df,
                    instruments,
                    date,
                    date_prev,
                    i,
                    historical_data,
                )
                # Obtain strategy scalar
                strat_scalar = backtest_utils.get_strat_scalar(
                    portfolio_df,
                    lookback=100,
                    vol_target=self.vol_target,
                    idx=i,
                    default=strat_scalar,
                )
                # now, our strategy leverage / scalar should dynamically
                # equilibrate to achieve target exposure

            portfolio_df.loc[i, "strat scalar"] = strat_scalar

            """
            Get Positions
            """
            for inst in non_tradeable:
                portfolio_df.loc[i, "{} units".format(inst)] = 0
                portfolio_df.loc[i, "{} w".format(inst)] = 0

            nominal_total = 0
            for inst in tradeable:
                """
                vote long if fastMA > slowMA else no vote

                We are trying to harvest momentum. We use MA pairs to proxy momentum,
                and define it's strength by fraction of trending pairs
                """
                votes = [
                    1
                    if (
                        historical_data.loc[date, "{} ema{}".format(inst, str(pair))]
                        > 0
                    )
                    else 0
                    for pair in self.pairs
                ]
                # degree of momentum measure from 0 to 1. 1 if all trending,
                # 0 if none trending
                forecast = np.sum(votes) / len(votes)
                # print("Forecast {}".format(forecast))
                forecast = (
                    0
                    if historical_data.loc[date, "{} adx".format(inst)] < 25
                    else forecast
                )  # if regime is not trending, set forecast to 9

                """
                Vol targeting
                """
                # vol targeting
                position_vol_target = (
                    (1 / len(tradeable))
                    * portfolio_df.loc[i, "capital"]
                    * self.vol_target
                    / np.sqrt(253)
                )
                inst_price = historical_data.loc[date, "{} close".format(inst)]
                percent_ret_vol = (
                    historical_data.loc[date, "{} % ret vol".format(inst)]
                    if (
                        historical_data.loc[:date]
                        .tail(20)["{} active".format(inst)]
                        .all()
                    )
                    else 0.025
                )

                dollar_volatility = (
                    inst_price * percent_ret_vol
                )  # vol in nominal dollar terms
                position = (
                    strat_scalar * forecast * position_vol_target / dollar_volatility
                )
                portfolio_df.loc[i, "{} units".format(inst)] = position
                # print(inst, position, forecast)
                nominal_total += abs(
                    position * inst_price
                )  # assuming no FX conversion is required

            for inst in tradeable:
                units = portfolio_df.loc[i, "{} units".format(inst)]
                nominal_inst = (
                    units * historical_data.loc[date, "{} close".format(inst)]
                )
                inst_w = nominal_inst / nominal_total
                portfolio_df.loc[i, "{} w".format(inst)] = inst_w

                """
                This means: if the asset has been actively traded 
                in the past 20 days, then use the rollign volatility 
                as measure of asset vol, else use default 0.025
                This is because, suppose an asset is not actively traded. 
                Then its vol would be low, since there is little movement. 
                Take an asset position inversley proportional to 
                vol -> then the asset position would be large, since the 
                reciprocal of vol is large. This would blow up the postion sizing!
                """

            """
            Perform Calculations for Date
            """
            portfolio_df.loc[i, "nominal"] = nominal_total
            portfolio_df.loc[i, "leverage"] = (
                nominal_total / portfolio_df.loc[i, "capital"]
            )
            print(portfolio_df.loc[i])

        self.save_df_to_tests_dir(portfolio_df)

    def get_subsys_pos(self):
        self.run_simulation(self.historical_df)
        pass

    def save_df_to_tests_dir(self, portfolio_df):
        root_project_path = Path(__file__).parent.parent.parent.resolve()
        tests_dir = Path(root_project_path, "tests")
        portfolio_df.to_excel(f"{tests_dir}/data/libmom.xlsx")
