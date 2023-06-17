import shioaji_realtime_kbars as shioaji_realtime_kbars
from shioaji import TickSTKv1, TickFOPv1, Exchange
import shioaji as sj
import pandas as pd

if __name__ == "__main__":
    api = sj.Shioaji()

    api.login(
        api_key="YOUR_API_KEY", 
        secret_key="YOUR_API_SECRET"
    )

    Contracts = shioaji_realtime_kbars.ShioajiRealtimeKbars(api)
    Contracts.subscribe(api.Contracts.Futures.MXF.MXFR1)
    Contracts.subscribe(api.Contracts.Futures.TXF.TXFR1)

    @api.on_tick_stk_v1()
    def callback(exchange: Exchange, tick : TickSTKv1):
        Contracts.update(tick, "stk")

    @api.on_tick_fop_v1()
    def callback(exchange : Exchange, tick : TickFOPv1):
        Contracts.update(tick, "fop")
        
    while True:
        MXFR1_1K = Contracts.kbars(api.Contracts.Futures.MXF.MXFR1, "1min")
        df = pd.DataFrame({**MXFR1_1K })
        df.ts = pd.to_datetime(df.ts)
        print(df.tail(2), end = "\n")
        MXFR1_5K = Contracts.kbars(api.Contracts.Futures.MXF.MXFR1, "5min")
        df = pd.DataFrame({**MXFR1_5K })
        df.ts = pd.to_datetime(df.ts)
        print(df.tail(2), end = "\n")