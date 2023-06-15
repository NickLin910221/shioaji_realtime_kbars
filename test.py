from realtime_kbars import Realtime_Contracts
from shioaji import TickSTKv1, TickFOPv1, Exchange, data
import shioaji as sj
import config
import pandas as pd


if __name__ == "__main__":
    api = sj.Shioaji()
    api.login(
        api_key=config.API_KEY, 
        secret_key=config.API_SECRET
    )

    Contracts = Realtime_Contracts(api)
    Contracts.subscribe(api.Contracts.Futures.MXF.MXFR1)
    Contracts.subscribe(api.Contracts.Futures.TXF.TXFR1)

    @api.on_tick_stk_v1()
    def callback(exchange: Exchange, tick : TickSTKv1):
        Contracts.update(tick, "stk")

    @api.on_tick_fop_v1()
    def callback(exchange : Exchange, tick : TickFOPv1):
        Contracts.update(tick, "fop")

    while True:
        MXFR1 = Contracts.Kbars(api.Contracts.Futures.MXF.MXFR1, "1min")
        df = pd.DataFrame({**MXFR1})
        df.ts = pd.to_datetime(df.ts)
        print(api.Contracts.Futures.MXF.MXFR1)
        print(df.tail(2), end = "\n")
        TXFR1 = Contracts.Kbars(api.Contracts.Futures.TXF.TXFR1, "5min")
        df = pd.DataFrame({**TXFR1})
        df.ts = pd.to_datetime(df.ts)
        print(api.Contracts.Futures.TXF.TXFR1)
        print(df.tail(2), end = "\n")