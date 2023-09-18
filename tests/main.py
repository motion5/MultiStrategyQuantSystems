import unittest
import system
import pandas as pd
import matplotlib.pyplot as plt


class TestLibmom(unittest.TestCase):
    def test_main(self):
        strat = system.main()

        self.assertEqual(strat, None)

    def test_math_looks_correct(self):
        strat = system.main()
        df = pd.read_excel("./libmom.xlsx")
        result_capital = df["capital"].iloc[-1]
        print("result cap", result_capital, type(result_capital))
        result_capital_ret = (1 + df["capital ret"]).cumprod().iloc[-1]
        print("result cap ret", result_capital_ret, type(result_capital_ret))

        df["capital"].plot()
        df["capital ret"].plot()
        plt.show()

        input("Press Enter to continue...")
        self.assertEqual(strat, None)
