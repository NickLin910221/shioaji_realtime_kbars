<br/>
<p align="center">
  <h3 align="center">Shioaji Realtime Kline Extension
</h3>

  <p align="center">
    An Extensions help you streaming with real-time data
    <br/>
    <br/>
  </p>
</p>

![Contributors](https://img.shields.io/github/contributors/NickLin910221/Shioaji_Realtime_Kline?color=dark-green) ![Stargazers](https://img.shields.io/github/stars/NickLin910221/Shioaji_Realtime_Kline?style=social) ![Issues](https://img.shields.io/github/issues/NickLin910221/Shioaji_Realtime_Kline) [![PyPI Latest Release](https://img.shields.io/pypi/v/shioaji-realtime-kbars.svg)](https://pypi.org/project/shioaji-realtime-kbars/) [![PyPI Downloads](https://img.shields.io/pypi/dm/shioaji-realtime-kbars.svg?label=PyPI%20downloads)](https://pypi.org/project/shioaji-realtime-kbars/)

## Table Of Contents

* [About the Project](#about-the-project)
* [Description](#description)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Version](#version)
* [Roadmap](#roadmap)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

When you use Shioaji Python API for technical analysis, you may need real-time data, and in different time dimensions, this package can help you subscribe to tick data and convert it into Kbars type (exactly the same as Shioaji Kbars ), to assist you in converting from Kbars to use more immediate data.

If you have any ideas or suggestions, we sincerely welcome you to contact us via email, or by creating an issue.

Assuming this project has been of great help to you, you are welcome to support my continued efforts through the following means.

[![Donate with PayPal](https://raw.githubusercontent.com/aha999/DonateButtons/master/Paypal.png)](https://www.paypal.me/yourui0221)

[
  ![Donate with PayPal]
  (https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png)
]
(https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QT54MSJR6QU7Y)

ETH : 0xb25aD6A441E89cFCa7850bA47A0d74131374d616

## Description

1. To use the extension just initialize the object
```
import shioaji_realtime_kbars
Contracts = shioaji_realtime_kbars.ShioajiRealtimeKbars(api)
```
2. Get the real-time Kbars data with function
```
shioaji_realtime_kbars.Kbars(
    contract: shioaji.contracts.BaseContract,
    period: str = '5min'
) -> shioaji.data.Kbars
```
:information_source: period format can refer to the [pandas document](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html).

:warning: If you using this extension, you start with the market is opened and transactions frequently time.
The latest Kline will be a little error.

Example :
I use this extension in 8:45:10 in future market.
The 8:46 Kline will have a little error.
Ths data after 8:47 will be correct.
So run this extension before the market is opened.

## Getting Started

This is an example of how you may give instructions on setting up your project locally.


```sh
pip install shioaji_realtime_kbars
```

## Usage

### kbars
Refer to the [shioaji sample](https://sinotrade.github.io/tutor/market_data/historical/#kbar)

```
import pandas as pd
kbars = api.kbars(
    contract=api.Contracts.Stocks["2330"], 
    start="2023-01-15", 
    end="2023-01-16", 
)
df = pd.DataFrame({**kbars})
df.ts = pd.to_datetime(df.ts)
df.tail(5)
```
Change to

```
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
```

### Callback funtion
```
shioaji_realtime_kbars.ShioajiRealtimeKbars.subscribe?

Signature:
shioaji_realtime_kbars.ShioajiRealtimeKbars.subscribe(
    contract: List[Union[shioaji.contracts.Option, shioaji.contracts.Future, shioaji.contracts.Stock, shioaji.contracts.Index]],
    last_days: int = 0,
    cb: Any = List[[callback_function, period]]
) -> None
```

### Example
If you want to clearly write your strategy. You can refer to example

```
def strategy(period, kbars):
    print(period)
    df = pd.DataFrame({**kbars}, columns = ["ts", "Open", "High", "Low", "Close", "Volume", "Amount"])
    df.ts = pd.to_datetime(df.ts)

    ### Write your strategy here ###

    print(df.tail(5), end = "\n")

if __name__ == "__main__":

    api = sj.Shioaji(simulation = True)

    api.login(
        api_key=config.API_KEY, 
        secret_key=config.API_SECRET
    )

    Contracts = shioaji_realtime_kbars.ShioajiRealtimeKbars(api)
    Contracts.subscribe(api.Contracts.Futures.MXF.MXFR1, last_days = 3, cb = [[strategy, "1min"], [strategy, "5min"]])

    @api.on_tick_fop_v1()
    def callback(exchange : Exchange, tick : TickFOPv1):
        Contracts.update(tick, "fop")

    Event().wait()
```


## Version
- v1.0.7 (2023/10/11) Add TSE, TFE simtrade filter, Fix kbars with no historical problem
- v1.0.6 (2023/7/28) Fis display
- v1.0.5 (2023/7/19) Add callback function
- v1.0.4 (2023/7/17)
- v1.0.3 (2023/6/30) Fix Stock kbars problem [issue](https://github.com/NickLin910221/shioaji_realtime_kbars/issues/1)
- v1.0.1 Fix Naming Problem
- v1.0.0

## Roadmap

See the [open issues](https://github.com/NickLin910221/Shioaji_Realtime_Kline/issues) for a list of proposed features (and known issues).

## Authors

* **You-rui, Lin** - ** - [You-rui, Lin](https://dearestbee.tplinkdns.com/Resume.pdf) - *Whole project*
