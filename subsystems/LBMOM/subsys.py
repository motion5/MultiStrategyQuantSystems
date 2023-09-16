import json
import quantlib.indicators_cal as indicators_cal
import pandas as pd


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
        print(historical_data)
        portfolio_df = pd.DataFrame(
            index=historical_data[self.simulation_start :].index
        ).reset_index()
        portfolio_df.loc[0, "capital"] = 10000
        print(portfolio_df)

        """
        Run Simulation
        """
        pass

    def get_subsys_pos(self):
        self.run_simulation(self.historical_df)
        pass

    """
    We are going to be using Asset management techniques called 
    'Volatility Targeting' - at both the asset level and the strategy level

    I've added notes to Obsidian for the intros to each of those articles
    and further reading which is useful, since HangukQuant doesn't make
    those articles avialable on his substack anymore

    We will also be using voting systems to account for the degree of expected
    returns. In particular, if there are more moving averages that indicate 
    momentum, then we want to bet bigger (use more risk)

    """
