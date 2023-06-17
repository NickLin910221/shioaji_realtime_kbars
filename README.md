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

![Contributors](https://img.shields.io/github/contributors/NickLin910221/Shioaji_Realtime_Kline?color=dark-green) ![Stargazers](https://img.shields.io/github/stars/NickLin910221/Shioaji_Realtime_Kline?style=social) ![Issues](https://img.shields.io/github/issues/NickLin910221/Shioaji_Realtime_Kline) 

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

## Description

1. To use the extension just initialize the object
```
import shioaji_realtime_kbars
Contracts = shioaji_realtime_kbars.shioaji_realtime_kbars(api)
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
        MXFR1_1K = Contracts.Kbars(api.Contracts.Futures.MXF.MXFR1, "1min")
        df = pd.DataFrame({**MXFR1_1K })
        df.ts = pd.to_datetime(df.ts)
        df.tail(5)
        MXFR1_5K = Contracts.Kbars(api.Contracts.Futures.MXF.MXFR1, "5min")
        df = pd.DataFrame({**MXFR1_5K })
        df.ts = pd.to_datetime(df.ts)
        df.tail(5)
```

## Version
### v1.0.1 
#### * Fix Naming Problem
### v1.0.0

## Roadmap

See the [open issues](https://github.com/NickLin910221/Shioaji_Realtime_Kline/issues) for a list of proposed features (and known issues).

## Authors

* **You-rui, Lin** - ** - [You-rui, Lin](https://dearestbee.tplinkdns.com/Resume.pdf) - *Whole project*
