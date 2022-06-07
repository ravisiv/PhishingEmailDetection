from sklearn.model_selection import train_test_split
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
import phdcommon as conf
warnings.filterwarnings('ignore')



def plot_confusion_matrix(cm, classes,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):

    print(cm)

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



#################################################Main Method##############################

masteremails = conf.get_target("masteremails")
df = pd.read_csv(masteremails)

# Removing all null columns
column = 0
describe_df = df.describe()
email_cols = df.columns
for each in describe_df.iloc[7]:
    if each == 0.0:
        del df[email_cols[column]]
    column += 1


missing_data_columns = df.columns[df.isnull().any()]

df.fillna(value=df.mode().iloc[0], inplace=True)

corr_df = pd.DataFrame(df_X.corr().abs())
upper_tri = corr_df.where(np.triu(np.ones(corr_df.shape), k=1).astype(np.bool))

to_drop = [column for column in upper_tri.columns if any(
    upper_tri[column] > 0.99)]

X = df.drop(['target'], axis=1)
ind_columns = df.drop('target', axis=1).columns
y = df['target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#Direct train/test split
X_train, X_test, Y_train, Y_test = train_test_split(
    X_scaled, y, test_size=0.20, stratify=y, random_state=1234
)

LR = LogisticRegression()

# define parameters
#penalty_LR = ['l1', 'l2', 'elasticnet', 'none'] 
penalty_LR = [ 'l1', 'l2'] 
C_LR = [0.001, 0.01, 0.1, 1, 10, 100, 1000]  
#C_LR = [0.001,10, 100]  
max_iter_LR = [500]
#max_iter_LR = [500]
class_weight_LR = ['balanced']
#solver_LR = ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']
solver_LR = ['lbfgs', 'liblinear']

# define random search
param_random_LR = dict(penalty=penalty_LR, C=C_LR, max_iter=max_iter_LR, class_weight=class_weight_LR, solver=solver_LR)


search_LR = RandomizedSearchCV(estimator=LR, param_distributions=param_random_LR, n_jobs=3, cv=cv, 
                               scoring='accuracy',n_iter=20, verbose=5)


result_LR = search_LR.fit(X_train, Y_train)
# summarize results
print("Best: %f using %s" % (result_LR.best_score_, result_LR.best_params_))
means = result_LR.cv_results_['mean_test_score']
stds = result_LR.cv_results_['std_test_score']
params = result_LR.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))
best_Estimator_LR = result_LR.best_estimator_
print("Best LR Results",best_Estimator_LR)

y_pred = best_Estimator_LR.predict(X_test)
acc_score = accuracy_score(y_pred, Y_test)
print("Accuracy Score",acc_score)
print(classification_report(Y_test, y_pred))


#### Neural Network Model
ensemble_model = tf.keras.Model()

layer_zero = tf.keras.Input(shape=(55,))
layer1 = tf.keras.layers.Dense(256, activation='swish')(layer_zero)
layer1_bn = tf.keras.layers.BatchNormalization()(layer1)
layer1_do = tf.keras.layers.Dropout(0.2)(layer1_bn)
layer2 = tf.keras.layers.Dense(1024, activation='swish')(layer1_do)
layer2_bn = tf.keras.layers.BatchNormalization()(layer2)
layer2_do = tf.keras.layers.Dropout(0.2)(layer2_bn)
layer3 = tf.keras.layers.Dense(256, activation='swish')(layer2_do)
layer3_do = tf.keras.layers.Dropout(0.2)(layer3)
layer4 = tf.keras.layers.Dense(128, activation='swish')(layer3_do)
layer4_do = tf.keras.layers.Dropout(0.2)(layer4)
layer5 = tf.keras.layers.Dense(2, activation='sigmoid')(layer4_do)

ensemble_model = tf.keras.Model(inputs=layer_zero, outputs=layer5)

inputs = tf.keras.Input(shape=(512,512,3))

ensemble_model.compile(optimizer=Adam(
), loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
safety = EarlyStopping(monitor='val_loss', patience=4, min_delta=2e-4)


x_train, x_val, y_train, y_val = train_test_split(
    X_train, Y_train, stratify=Y_train, test_size=0.2, random_state=1234)

print(ensemble_model.summary())

nn_history = ensemble_model.fit(x_train, y_train,
                          validation_data=(x_val, y_val),
                          callbacks=[tb, safety],
                          epochs=200, batch_size=25
                          )

y_pred = ensemble_model.predict(X_test)

print(classification_report(Y_test, np.argmax(y_pred, axis=1)))

cm = confusion_matrix(Y_test, np.argmax(y_pred, axis=1))
cm_plot_label = [0, 1]
plot_confusion_matrix(cm, cm_plot_label, title='Confusion Matrix')

print("The Enc.")
