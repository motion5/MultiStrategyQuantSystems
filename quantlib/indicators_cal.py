"""
A calculator for indicators and other functionalities
"""

# we need a dependency ta-lib for this, we can install on MacOS with brew install ta-lib

import numpy as np
import pandas as pd
import talib  # type: ignore


def adx_series(high, low, close, n):
    return talib.ADX(high, low, close, timeperiod=n)  # type: ignore


def ema_series(series, n):
    return talib.EMA(series, timeperiod=n)  # type: ignore


def sma_series(series, n):
    return talib.SMA(series, timeperiod=n)  # type: ignore
