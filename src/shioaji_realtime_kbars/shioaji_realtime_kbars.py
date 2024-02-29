import shioaji as sj
import datetime as dt
import math
import pandas as pd
from shioaji.data import Kbars

class RealtimeKbars(Kbars):
    
    def update(self, data):
        if len(self.ts) == 0:
            self.ts.append(data["ts"])
            self.Open.append(data["Close"])
            self.High.append(data["Close"])
            self.Low.append(data["Close"])
            self.Close.append(data["Close"])
            self.Volume.append(data["Volume"])
            self.Amount.append(data["Amount"])
        elif self.ts[-1] < data["ts"]:
            self.ts.append(data["ts"])
            self.Open.append(data["Close"])
            self.High.append(data["Close"])
            self.Low.append(data["Close"])
            self.Close.append(data["Close"])
            self.Volume.append(data["Volume"])
            self.Amount.append(data["Amount"])
        else:
            self.High[-1] = max(self.High[-1], data["Close"])
            self.Low[-1] = min(self.Low[-1], data["Close"])
            self.Close[-1] = data["Close"]
            self.Volume[-1] += data["Volume"]
            self.Amount[-1] += data["Amount"]
        return
    
    def getKlines(self, period):
        ts = [int(x) for x in self.ts]
        kbars_list = list(zip(ts, self.Open, self.High, self.Low, self.Close, self.Volume, self.Amount))
        kbars_df = pd.DataFrame(kbars_list, columns=["ts", "Open", "High", "Low", "Close", "Volume", "Amount"])
        kbars_df.ts = pd.to_datetime(kbars_df.ts)
        kbars_df = kbars_df.set_index(kbars_df.ts)
        kbars_df = kbars_df.resample(f'{period}', closed='right', label='right').apply({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum', 'Amount': 'sum'})
        kbars_df = kbars_df.dropna(subset=['Open', 'High', 'Low', 'Close'])

        return kbars_df

class Contracts:

    __slots__ = ["api", "contract", "last_days", "kbars", "cache", "response", "cb"]

    def __init__(self, api, contract, cb, last_days = 0):
        self.api = api
        self.contract = contract
        self.last_days = last_days
        self.fetchdata()
        self.subscribe()
        self.cb = cb

    def fetchdata(self):
        res = self.api.kbars(
            contract = self.contract, 
            start = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(days = self.last_days), "%Y-%m-%d"), 
            end = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")
        )
        self.kbars = RealtimeKbars(**res)
        self.response = Kbars(**res)

    def subscribe(self):
        self.api.quote.subscribe(
            contract = self.contract,
            quote_type = sj.constant.QuoteType.Tick,
            version = sj.constant.QuoteVersion.v1
        )

    def update(self, tick):
        if tick.simtrade == 1: return
        self.kbars.update({"ts" : (math.floor(int(tick.datetime.replace(tzinfo=dt.timezone.utc).timestamp() * 1000000000) / 60000000000) + 1) * 60000000000, "Open" : float(tick.open), "High" : float(tick.high), "Low" : float(tick.low), "Close" : float(tick.close), "Volume" :  tick.volume, "Amount" : float(tick.amount)})
        for cb, period in self.cb:
            cb(period, self.getklines(period))

    def getklines(self, period):
        res                     = self.kbars.getKlines(period)
        self.response.ts        = res.index.values.tolist()
        self.response.Open      = res["Open"].values.tolist()
        self.response.High      = res["High"].values.tolist()
        self.response.Low       = res["Low"].values.tolist()
        self.response.Close     = res["Close"].values.tolist()
        self.response.Volume    = res["Volume"].values.tolist()
        self.response.Amount    = res["Amount"].values.tolist()
        return self.response
    
class ShioajiRealtimeKbars():

    __slots__ = ["api", "stk_Contracts", "fop_Contracts"]

    def __init__(self, api):
        self.api = api
        self.stk_Contracts, self.fop_Contracts = [], []

    def subscribe(self, contract, last_days = 0, cb = []):
        if contract.__class__ is sj.contracts.Stock:
            for _contract_ in self.stk_Contracts:
                if contract.code == _contract_.contract.code: return
            self.stk_Contracts.append(Contracts(self.api, contract, last_days = last_days, cb = cb))    
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            for _contract_ in self.fop_Contracts:
                if contract.target_code == _contract_.contract.target_code or contract.code == _contract_.contract.code: return
            self.fop_Contracts.append(Contracts(self.api, contract, last_days = last_days, cb = cb))
            
    def update(self, tick, type):
        if type == "stk":
            for _contract_ in self.stk_Contracts:
                if tick.code == _contract_.contract.code: _contract_.update(tick)
        elif type == "fop":
            for _contract_ in self.fop_Contracts:
                if tick.code == _contract_.contract.target_code or tick.code == _contract_.contract.code: _contract_.update(tick)
    
    def kbars(self, contract, period):
        if contract.__class__ is sj.contracts.Stock:
            for _contract_ in self.stk_Contracts:
                if contract.code == _contract_.contract.code: return _contract_.getklines(period)
            return Kbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = []) 
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            for _contract_ in self.fop_Contracts:
                if contract.code == _contract_.contract.code: return _contract_.getklines(period)
            return Kbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = [])