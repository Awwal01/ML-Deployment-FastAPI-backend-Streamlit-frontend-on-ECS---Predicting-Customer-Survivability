
import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator


class age_sex_transformer(BaseEstimator):
    def __init__(self):
        pass

    def fit(self, documents, y=None):
        return self

    def transform(self, x_dataset):
        sex_mapping = {'male': 0, 'female':1}
        bins = [0, 5, 12, 18, 24, 35, 60, np.inf]
        labels = [1, 2, 3, 4, 5, 6,7]
        x_dataset['Sex'] = x_dataset['Sex'].map(sex_mapping)
        x_dataset['AgeGroup'] = pd.cut(x_dataset['Age'], 
                                       bins, 
                                       right=False,
                                       labels=labels)
        x_dataset = x_dataset.dropna()

        return x_dataset[['Pclass', 'Sex', 'AgeGroup']]
