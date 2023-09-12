import pandas as pd
import quantlib.general_uitls as gu
import quantlib.data as data

#df, instruments = data.get_sp500_df()
#df = data.extend_dataframe(instruments, df) 
#gu.save_file("./Data/data.obj", (df, instruments))
#gu.save_file("./Data/data.obj", (df, instruments))

df, instruments = gu.load_file("./Data/data.obj")
print(df, instruments)

# We will straight into implementing a stragegy, we call this LBMOM for long biased momentum
# We call the other LSMOM for Long short momentum

