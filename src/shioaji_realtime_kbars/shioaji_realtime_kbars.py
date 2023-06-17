import shioaji as sj
import datetime as dt
import math
import pandas as pd
from shioaji import data

class realtime_Kbars(data.Kbars):
    def update(self, data):
        if self.ts[-1] < data["ts"]:
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
        kbars = data.Kbars(ts = kbars_df.index.values.tolist(), 
                           Open = kbars_df["Open"].values.tolist(), 
                           High = kbars_df["High"].values.tolist(), 
                           Low = kbars_df["Low"].values.tolist(), 
                           Close = kbars_df["Close"].values.tolist(), 
                           Volume = kbars_df["Volume"].values.tolist(), 
                           Amount = kbars_df["Amount"].values.tolist())
        return kbars

class RealtimeKbars:
    __slots__ = ["api", "contract", "last_days", "kbars", "cache"]

    def __init__(self, api, contract, last_days = 0):
        self.api = api
        self.contract = contract
        self.last_days = last_days
        self.fetchdata()
        self.subscribe()

    def fetchdata(self):
        res = self.api.kbars(
            contract = self.contract, 
            start = dt.datetime.strftime(dt.datetime.today() - dt.timedelta(days = self.last_days), "%Y-%m-%d"), 
            end = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")
        )
        self.kbars = realtime_Kbars(**res)        

    def subscribe(self):
        self.api.quote.subscribe(
            contract = self.contract,
            quote_type = sj.constant.QuoteType.Tick,
            version = sj.constant.QuoteVersion.v1
        )

    def update(self, tick):
        self.kbars.update({"ts" : (math.floor(int(tick.datetime.replace(tzinfo=dt.timezone.utc).timestamp() * 1000000000) / 60000000000) + 1) * 60000000000, "Open" : float(tick.open), "High" : float(tick.high), "Low" : float(tick.low), "Close" : float(tick.close), "Volume" :  tick.volume, "Amount" : float(tick.amount)})

    def getKlines(self, period):
        return self.kbars.getKlines(period)
    
class shioaji_realtime_kbars():
    __slots__ = ["api", "stk_Contracts", "fop_Contracts"]
    def __init__(self, api):
        self.api = api
        self.stk_Contracts, self.fop_Contracts = [], []

    def subscribe(self, contract, last_days = 0):
        if contract.__class__ is sj.contracts.Stock:
            for _contract_ in self.stk_Contracts:
                if contract.contract.code == _contract_.contract.code: return
            self.stk_Contracts.append(RealtimeKbars(self.api, contract, last_days = last_days))    
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            for _contract_ in self.fop_Contracts:
                if contract.target_code == _contract_.contract.target_code or contract.code == _contract_.contract.code: return
            self.fop_Contracts.append(RealtimeKbars(self.api, contract, last_days = last_days))
            
    def update(self, tick, type):
        if type == "stk":
            for _contract_ in self.stk_Contracts:
                if tick.code == _contract_.contract.code: _contract_.update(tick)
        elif type == "fop":
            for _contract_ in self.fop_Contracts:
                if tick.code == _contract_.contract.target_code or tick.code == _contract_.contract.code: _contract_.update(tick)
    
    def Kbars(self, contract, period):
        if contract.__class__ is sj.contracts.Stock:
            for _contract_ in self.stk_Contracts:
                if contract.contract.code == _contract_.contract.code: return _contract_.getKlines(period)
            return data.Kbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = []) 
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            for _contract_ in self.fop_Contracts:
                if contract.code == _contract_.contract.code: return _contract_.getKlines(period)
            return data.Kbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = [])