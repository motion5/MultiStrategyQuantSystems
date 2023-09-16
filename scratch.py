import json
import random
from typing import List, Tuple

# We will straight into implementing a stragegy,
# we call this LBMOM for long biased momentum
# We call the other LSMOM for Long short momentum
pairs: List[Tuple[int, int]] = []
while len(pairs) <= 20:
    """
    # from paper:
    Let's say that the rolling windows may reasonably range from 16 to 300 days.

    Then, we sample 2 numbers from this range 20 times to obtain 20 different pairs
    of entry/exit rules to get 20 Moving Average Crossover Strategies. We go long if
    the FastMA > SlowMA and otherwise stay in cash. In addition, we also simulate another
    strategy where we take a combination of the signals from each of these 20 signals in a
    voting system, such that we have the full position on if all 20 are "trending', half
    the full sizing if only 20 are trending etcetera.

    We control for volatility, such that each of these 21 backtests have identical
    annualised volatility/risk levels, such that their returns are independent of Leverage.
    """

    # We do the initalisation of the pairs by randomly
    # sampling from a range of suitable values

    # we then take the minimum of the two as the fast-moving-average,
    # and the maximum of the slow moving average
    pair = random.sample(list(range(16, 300)), 2)
    if pair[0] == pair[1]:
        continue
    pairs.append((min(pair[0], pair[1]), max(pair[0], pair[1])))
print(pairs)  # these lines are the moving average crossover rules


## getting json
with open("./subsystems/LBMOM/config.json", "w") as f:
    json.dump({"instruments": instruments}, f, indent=4)
