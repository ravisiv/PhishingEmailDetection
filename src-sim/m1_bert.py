import phdcommon as conf
import yaml
import xgboost as xgb
import warnings
import tensorflow as tf
import sys
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import datetime as dt
from time import time
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics as mt


#/Users/ravis/Downloads/reduceddata/models/bert/bert_model

#!/usr/bin/env python
# coding: utf-8


def get_m7_urlmeta_data(src_df):
    ret_df = src_df[['topdomain1', 'topdomain2', 'topdomain3', 'topdomain4', 'topdomain5', 'topdomain6', 'topdomain7', 'topdomain8', 'topdomain9', 'topdomain10', 'topdomain11',
                     'subdomain1', 'subdomain2', 'subdomain3', 'subdomain4', 'subdomain5', 'subdomain6', 'subdomain7', 'subdomain8', 'subdomain9', 'subdomain10', 'subdomain11',
                     'suffix1', 'suffix2', 'suffix3', 'suffix4', 'suffix5', 'suffix6', 'suffix7', 'suffix8', 'suffix9', 'suffix10', 'suffix11', 'bert_urgency'
                     ]]
    return ret_df


########################################################Main Method#############################################
# load data
if len(sys.argv) < 2:
    print("Data file required")
    exit(0)
data_file = sys.argv[1]
df = pd.read_csv(data_file)  # read in the csv file

#Visualizing the hist of data to check normality of independent variable
df_X = df.drop(['bodytext'], axis=1)
#https://www.projectpro.io/recipes/drop-out-highly-correlated-features-in-python

corr_df = pd.DataFrame(df_X.corr().abs())

# Multi Colliniarity analysis on Independent variables
upper_tri = corr_df.where(np.triu(np.ones(corr_df.shape), k=1).astype(np.bool))
to_drop = [column for column in upper_tri.columns if any(
    upper_tri[column] > 0.99)]

#X = df.drop(['status', 'url'], axis=1).values
X = get_m7_urlmeta_data(df)
ind_columns = df.drop('target', axis=1).columns
y = df['target']
# We did normalize the attributes using StandardScaler() to scale them between 0 and 1 before running models.
# Normalize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#Direct train/test split
X_train, X_test, Y_train, Y_test = train_test_split(
    X_scaled, y, test_size=0.20, stratify=y, random_state=1234
)
#Create Cross Validation Procedure
cv = StratifiedKFold(n_splits=10, random_state=1234, shuffle=True)

# ### Model Building
# ##### Helper Function


def plot_confusion_matrix(cm, classes,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=55)
    plt.yticks(tick_marks, classes)
    #fmt = '.2f''d'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j]),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()


# #### Neural Network Model
x_train, x_val, y_train, y_val = train_test_split(
    X_train, Y_train, stratify=Y_train, test_size=0.2, random_state=1234)

url_model = tf.keras.Model()
layer_zero = tf.keras.Input(shape=(x_train.shape[1],))
layer1 = tf.keras.layers.Dense(256, activation='relu')(layer_zero)
layer1_bn = tf.keras.layers.BatchNormalization()(layer1)
layer1_do = tf.keras.layers.Dropout(0.2)(layer1_bn)
layer2 = tf.keras.layers.Dense(1024, activation='relu')(layer1_do)
layer2_bn = tf.keras.layers.BatchNormalization()(layer2)
layer2_do = tf.keras.layers.Dropout(0.2)(layer2_bn)
layer3 = tf.keras.layers.Dense(2048, activation='relu')(layer2_do)
layer3_do = tf.keras.layers.Dropout(0.2)(layer3)
layer4 = tf.keras.layers.Dense(128, activation='relu')(layer3_do)
layer4_do = tf.keras.layers.Dropout(0.2)(layer4)
layer5 = tf.keras.layers.Dense(2, activation='sigmoid')(layer4_do)

url_model = tf.keras.Model(inputs=layer_zero, outputs=layer5)
url_model.compile(optimizer=Adam(
), loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
safety = EarlyStopping(monitor='val_loss', patience=4, min_delta=2e-4)
nn_history = url_model.fit(x_train, y_train,
                           validation_data=(x_val, y_val),
                           callbacks=[safety],
                           epochs=200, batch_size=25)


target_dir = conf.get_target("modeldir")
model_folder = f"{target_dir}/m5-urlmeta"
url_model.save(model_folder)
print("External m5-urlmeta neural network saved:", model_folder)
