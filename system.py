import quantlib.general_uitls as gu

import quantlib.data as data
from dateutil.relativedelta import relativedelta
from subsystems.LBMOM.subsys import Libmom

import pandas as pd
from warnings import simplefilter

# Supress concat pandas warning - super annoying
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

# df, instruments = data.get_sp500_df()
# df = data.extend_dataframe(traded=instruments, df=df)
# df.to_excel("./Data/hist-30-inst.xlsx")
# gu.save_file("./Data/data-30-inst.obj", (df, instruments))
# gu.save_file("./Data/data.obj", (df, instruments))

# Lecture
# with open("./subsystems/LBMOM/config.json", "w") as f:
#    json.dump({"instruments": instruments}, f, indent=4)


def main():
    df, instruments = gu.load_file("./Data/data-30-inst.obj")
    print(df, instruments)
    # df.to_csv("./Data/data-30-inst.csv")

    # run simulation for 5 years
    VOL_TARGET = 0.20
    print(df.index[-1])  # date today: 2023-09-14
    sim_start = df.index[-1] - relativedelta(months=1)
    print(sim_start)

    strat = Libmom(
        instruments_config="./subsystems/LBMOM/config-30-inst.json",
        historical_df=df,
        simulation_start=sim_start,
        vol_target=VOL_TARGET,
    )

    strat.get_subsys_pos()
    """
    """
    return
