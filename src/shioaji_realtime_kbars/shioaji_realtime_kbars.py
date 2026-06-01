import shioaji as sj
import datetime as dt
import math
import pandas as pd
import threading

__SJ_VERSION__ = sj.__version__

if __SJ_VERSION__ == "1.5.0":
    raise ImportError("ShioajiRealtimeKbars requires Shioaji version > 1.5.0")

class RealtimeKbars():
    def __init__(self, ts, Open, High, Low, Close, Volume, Amount, **kwargs):
        self.ts = list(ts)
        self.Open = list(Open)
        self.High = list(High)
        self.Low = list(Low)
        self.Close = list(Close)
        self.Volume = list(Volume)
        self.Amount = list(Amount)

    def keys(self):
        return ["ts", "Open", "High", "Low", "Close", "Volume", "Amount"]

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, data):
        close = data["Close"]
        if not self.ts or self.ts[-1] < data["ts"]:
            self.ts.append(data["ts"])
            self.Open.append(close)
            self.High.append(close)
            self.Low.append(close)
            self.Close.append(close)
            self.Volume.append(data["Volume"])
            self.Amount.append(data["Amount"])
        else:
            if close > self.High[-1]: self.High[-1] = close
            elif close < self.Low[-1]: self.Low[-1] = close
            self.Close[-1] = close
            self.Volume[-1] += data["Volume"]
            self.Amount[-1] += data["Amount"]

    def getKlines(self, period):
        kbars_df = pd.DataFrame({
            "ts": self.ts,
            "Open": self.Open,
            "High": self.High,
            "Low": self.Low,
            "Close": self.Close,
            "Volume": self.Volume,
            "Amount": self.Amount,
        })
        kbars_df["ts"] = pd.to_datetime(kbars_df["ts"].astype("int64"))
        kbars_df = kbars_df.set_index("ts")
        kbars_df = kbars_df.resample(period, closed='right', label='right').agg(
            {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum', 'Amount': 'sum'}
        ).dropna(subset=['Open', 'High', 'Low', 'Close'])
        return kbars_df

class Contracts:

    __slots__ = ["api", "contract", "last_days", "kbars", "cache", "response", "cb", "_lock"]

    def __init__(self, api, contract, cb, last_days = 0):
        self._lock = threading.Lock()
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
        self.response = RealtimeKbars(**res)

    def subscribe(self):
        if __SJ_VERSION__ >= "1.5.0":
            self.api.subscribe(
                contract=self.contract,
                quote_type=sj.QuoteType.Tick,
                version=sj.QuoteVersion.v1,
            )
        else:
            self.api.quote.subscribe(
                contract = self.contract,
                quote_type = sj.constant.QuoteType.Tick,
                version = sj.constant.QuoteVersion.v1
            )

    def update(self, tick):
        if tick.simtrade == 1: return
        
        with self._lock:
            self.kbars.update({
                "ts" : (math.floor(int(tick.datetime.replace(tzinfo=dt.timezone.utc).timestamp() * 1000000000) / 60000000000) + 1) * 60000000000, 
                "Open" : float(tick.open), 
                "High" : float(tick.high), 
                "Low" : float(tick.low), 
                "Close" : float(tick.close), 
                "Volume" :  tick.volume, 
                "Amount" : float(tick.amount)
            })

        for cb, period in self.cb:
            cb(period, self.getklines(period))

    def getklines(self, period):
        with self._lock:
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
            return RealtimeKbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = [])
        elif contract.__class__ is sj.contracts.Future or contract.__class__ is sj.contracts.Option:
            for _contract_ in self.fop_Contracts:
                if contract.code == _contract_.contract.code: return _contract_.getklines(period)
            return RealtimeKbars(ts = [], Open = [], High = [], Low = [], Close = [], Volume = [], Amount = [])