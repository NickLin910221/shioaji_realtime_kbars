<<<<<<< HEAD
import shioaji as sj
from threading import Event
import datetime as dt
import math
import pandas as pd
from shioaji import TickSTKv1, BidAskSTKv1, TickFOPv1, BidAskFOPv1, Exchange

api = sj.Shioaji()
api.login(
    api_key="YOUR_API_KEY", 
    secret_key="YOUR_API_SECRET"
)

class RealtimeKbars:
    __slots__ = ["contract", "kbars", "K"]

    def __init__(self, shioaji, contract, K, amount):
        self.contract = contract
        self.K = K
        if contract.__class__ is sj.contracts.Stock:
            days = math.ceil(K * amount / 300) + 1
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            days = math.ceil(K * amount / 1260) + 1
        self.fetchdata(shioaji, contract, days)
        self.subscribedata(shioaji, contract)

    def fetchdata(self, shioaji, contract, days):
        res = shioaji.kbars(
            contract = contract, 
            start = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(days=days), "%Y-%m-%d"), 
            end = dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), "%Y-%m-%d")
        )
        res.ts = [int(x / 1000000) for x in res.ts]
        kbars_list = list(zip(res.ts, res.Open, res.High, res.Low, res.Close, res.Volume, res.Amount))
        kbars_df = pd.DataFrame(kbars_list)
        result = kbars_df.set_index(0)
        ohlc_dict = {'1': 'first', '2': 'max', '3': 'min', '4': 'last', '5': 'sum'}
        result = result.resample(f'{self.K}T', closed='right', label='right').apply(ohlc_dict)
        
        

    def subscribedata(self, shioaji, contract):
        shioaji.quote.subscribe(
            contract = contract,
            quote_type = sj.constant.QuoteType.Tick,
            version = sj.constant.QuoteVersion.v1
        )

    @api.on_tick_stk_v1(bind=True)
    def callback(self, exchange: Exchange, tick : TickSTKv1):
        print("ts", tick.datetime.timestamp() * 1000000000, "close", tick.close, "volume", tick.volume)

    @api.on_tick_fop_v1(bind=True)
    def callback(self, exchange : Exchange, tick : TickFOPv1):
        # print("ts", str(tick.datetime.timestamp() * 1000000000), "close", tick.close, "volume", tick.volume)
        ts = tick.datetime.replace(tzinfo=dt.timezone.utc).timestamp() * 1000
        print("ts %d, close %.1f volume %.1f" % (ts, tick.close, tick.volume))
        print(ts)
    def K_chart(self):
        return self.kbars

    def new_K(self, last = 1):
        return self.kbars[-last]

delta = RealtimeKbars(api, api.Contracts.Stocks.TSE.TSE2308, 15, 500)
chart = delta.K_chart()

MXF2023 = RealtimeKbars(api, api.Contracts.Futures.MXF.MXF202303, 15, 500)
chart = MXF2023.K_chart()

new_K = MXF2023.new_K(1)
print(new_K)

=======
import shioaji as sj
from threading import Event
import datetime as dt
import math
import pandas as pd
from shioaji import TickSTKv1, BidAskSTKv1, TickFOPv1, BidAskFOPv1, Exchange

api = sj.Shioaji()
api.login(
    api_key="3oH9ww2XZrRqTwmH44gA7XYfZMNr8cu2ktkdZuMuW2fL", 
    secret_key="9Xu1XMHBwFmWK9gMkkerEHS1AsdsLnYSyFbCxUjZ2U8X"
)

class RealtimeKbars:
    __slots__ = ["contract", "kbars", "K"]

    def __init__(self, shioaji, contract, K, amount):
        self.contract = contract
        self.K = K
        if contract.__class__ is sj.contracts.Stock:
            days = math.ceil(K * amount / 300) + 1
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            days = math.ceil(K * amount / 1260) + 1
        self.fetchdata(shioaji, contract, days)
        self.subscribedata(shioaji, contract)

    def fetchdata(self, shioaji, contract, days):
        res = shioaji.kbars(
            contract = contract, 
            start = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(days=days), "%Y-%m-%d"), 
            end = dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), "%Y-%m-%d")
        )
        res.ts = [int(x / 1000000) for x in res.ts]
        kbars_list = list(zip(res.ts, res.Open, res.High, res.Low, res.Close, res.Volume, res.Amount))
        kbars_df = pd.DataFrame(kbars_list)
        result = kbars_df.set_index(0)
        ohlc_dict = {'1': 'first', '2': 'max', '3': 'min', '4': 'last', '5': 'sum'}
        result = result.resample(f'{self.K}T', closed='right', label='right').apply(ohlc_dict)
        
        

    def subscribedata(self, shioaji, contract):
        shioaji.quote.subscribe(
            contract = contract,
            quote_type = sj.constant.QuoteType.Tick,
            version = sj.constant.QuoteVersion.v1
        )

    @api.on_tick_stk_v1(bind=True)
    def callback(self, exchange: Exchange, tick : TickSTKv1):
        print("ts", tick.datetime.timestamp() * 1000000000, "close", tick.close, "volume", tick.volume)

    @api.on_tick_fop_v1(bind=True)
    def callback(self, exchange : Exchange, tick : TickFOPv1):
        # print("ts", str(tick.datetime.timestamp() * 1000000000), "close", tick.close, "volume", tick.volume)
        ts = tick.datetime.replace(tzinfo=dt.timezone.utc).timestamp() * 1000
        print("ts %d, close %.1f volume %.1f" % (ts, tick.close, tick.volume))
        print(ts)
    def K_chart(self):
        return self.kbars

    def new_K(self, last = 1):
        return self.kbars[-last]

delta = RealtimeKbars(api, api.Contracts.Stocks.TSE.TSE2308, 15, 500)
chart = delta.K_chart()

MXF2023 = RealtimeKbars(api, api.Contracts.Futures.MXF.MXF202303, 15, 500)
chart = MXF2023.K_chart()

new_K = MXF2023.new_K(1)
print(new_K)

>>>>>>> ac995323f2b574172fdd73331c8d539276cd1752
Event().wait()