import quantlib.general_uitls as gu

from dateutil.relativedelta import relativedelta

from subsystems.LBMOM.subsys import Libmom

df, instruments = gu.load_file("./Data/data.obj")
print(df, instruments)

# run simulation for 5 years
VOL_TARGET = 0.20
print(df.index[-1])  # date today: 2023-09-14
sim_start = df.index[-1] - relativedelta(years=5)
print(sim_start)


strat = Libmom(
    instruments_config="./subsystems/LBMOM/config.json",
    historical_df=df,
    simulation_start=sim_start,
    vol_target=VOL_TARGET,
)

strat.get_subsys_pos()
