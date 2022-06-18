import pandas as pd
import datetime as dt
import numpy as np
from IPython.display import display
import warnings
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
from time import time
from sklearn.metrics import confusion_matrix
import itertools
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt
from sklearn import metrics as mt
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import accuracy_score
warnings.filterwarnings('ignore')

# read in the csv file
df = pd.read_csv( 'data/URLs.csv')
df_X = df.drop(['status'], axis=1)

corr_df = pd.DataFrame(df_X.corr().abs())
corr_df.head(100)

upper_tri = corr_df.where(np.triu(np.ones(corr_df.shape), k=1).astype(np.bool))
to_drop = [column for column in upper_tri.columns if any(
    upper_tri[column] > 0.99)]

df['status'].replace(['legitimate', 'phishing'],
                     [0, 1], inplace=True)

X = df.drop(['status', 'url'], axis=1)
ind_columns = df.drop('status', axis=1).columns
y = df['status']

# Normalize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
