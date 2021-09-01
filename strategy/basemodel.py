import os
import pickle

from src.static import Action

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, AdaBoostRegressor, StackingRegressor, \
    AdaBoostRegressor
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn import svm

from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


class BaseModel():
    def __init__(self):
        try:
            with open(f'{os.path.dirname(__file__)}/2Diff_ML-WORKING_model.pickle', 'rb') as f:
                self.ml_model = pickle.load(f)
        except:
            raise RuntimeError('Can not read model file')

    def _make_xy_from_data(self, data, feature_names):
        X = data[feature_names]
        y = data['result']
        y_clf = y > -0.003
        return X, y, y_clf

    def _make_data_set(self, d1):
        def z(s, p=70):
            return (s - s.rolling(p).mean()) / s.rolling(p).std()

        def minmax(s, p=70):
            return (s - s.rolling(p).min()) / (s.rolling(p).max() - s.rolling(p).min())

        data = d1.copy()
        close = data['close']
        data['price'] = close

        indicator1 = close.rolling(8).mean().diff(1)
        indicator2 = close.rolling(15).mean().diff(1).diff(1)

        data['indicator1'] = z(indicator1, p=90)
        data['indicator2'] = z(indicator2, p=90)
        data['indicator3'] = z(close.pct_change(1), p=90)

        std_s = close.rolling(8).mean().rolling(15).std() / close.rolling(8).mean()
        data['std_s'] = std_s

        data['result'] = data['close'].pct_change(7).shift(-7)

        feature_names = [f'indicator1',
                         f'indicator2',
                         f'indicator3',
                         f'std_s'
                         ]
        feature_filter_names = [f'price']

        data = data[feature_names + feature_filter_names + ['result']]

        return data, feature_names

    def get_value_pos(self, data):
        data, feature_names = self._make_data_set(data)
        data = data.fillna(0)
        X, y, y_clf_test = self._make_xy_from_data(data, feature_names)

        res = pd.Series(self.ml_model.predict(X.iloc[-1:]))[0]
        value_pos = (abs(res) * 130) ** (1.0)
        return value_pos

    def analyse_open(self, data):
        d1 = data

        data, feature_names = self._make_data_set(d1)
        data = data.fillna(0)

        X, y, y_clf_test = self._make_xy_from_data(data, feature_names)

        res = pd.Series(self.ml_model.predict(X.iloc[-1:]))[0]
        B = 0.00065

        filter_pos = data[f'std_s'].iloc[-1] > 0.009
        filter_pos = filter_pos and ((data['indicator3'].abs()).iloc[-1] > 1.55)

        if not filter_pos:
            return Action.HOLD

        if res > B:
            return Action.LONG
        elif res < B:
            return Action.SHORT
        else:
            return Action.HOLD

    def analyse_close(self, data, open_price, side):
        # never close based on data
        return Action.HOLD
