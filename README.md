# UnifiedTrader

UnifiedTrader is a Python app that allows you to quickly deploy your trading systems.

## Installation

1. Clone repository
2. Use pip to install depedencies
```bash
pip3 install -r requirements.txt
```

## Usage

- Change logic of openning and closing positions:
   - Override functions in `strategy/basemodel.py`
      - Upload pickle model to `strategy/` if needed
   - Edit in `src/algorithm.py` if needed

- Connect to a custom exchange or broker (current version works with *Binance* to load data and *FTX* to execute orders):
   - Override functions in `src/exchangeconnector.py`
   - If you haven't change the exchange, create `service_files/api_keys.ini`:
      ```ini
      [DEFAULT]
      api_key = "your api key"
      api_secret = "your secret key"
      subaccount_name = "subaccount name"
      ```
- Change **margin_rate_border** arg to a custom value for `self.position_reducer` in `src/app.py`:
   ```python
   self.position_reducer = PositionReducer(self.ctx,
                                                self.exchangeconnector,
                                                self.storage,
                                                margin_rate_border=<your margin rate value>)
   ```
   - **Position reducer** instance closes the oldest position if account margin rate is below margin_rate_border. You can override its logic in `processes/position_reducer.py`
   
- Set **test** arg to **False** for `self.exchangeconnector` and `self.algorithm` in `src/app.py`:
   ```python
   self.exchangeconnector = ExchangeConnector(test=False)
   self.algorithm = Algorithm(test=False)
   ```
- **Run the app and raise some money!**
   ```bash
   python3 main.py
   ```
 
