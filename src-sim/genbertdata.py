from tensorflow import constant, string
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Input
import tensorflow_text as text
import tensorflow_hub as hub
import tensorflow as tf
import phdcommon as conf
import pandas as pd


masteremail = conf.get_target("masteremails")
df = pd.read_csv(masteremail, usecols=['body_text', 'target'])

df = df.dropna()

X_train, X_test, y_train, y_test = train_test_split(
    df['body_text'], df['target'], stratify=df['target'])

preprocess = hub.KerasLayer(
    "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
encoder = hub.KerasLayer(
    "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4", trainable=False)


# Reference : https://becominghuman.ai/sequential-vs-functional-model-in-keras-20684f766057

# Bert layers
text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessed_text = preprocess(text_input)
outputs = encoder(preprocessed_text)
es = EarlyStopping(patience=2)
pooled_output = outputs["pooled_output"]  # [batch_size, 768].

# Neural network layers
#layer1 = tf.keras.layers.Dropout(0.1, name="dropout")(pooled_output)
#layer2= tf.keras.layers.Dense(512, activation='relu')(pooled_output)
#layer3 = tf.keras.layers.Dense(128, activation='relu')(pooled_output)
#layer4 = tf.keras.layers.Dense(1, activation='sigmoid', name="output")(layer3)


#layer1 = tf.keras.layers.Dense(256, activation='swish')(pooled_output)
#layer1_bn = tf.keras.layers.BatchNormalization()(layer1)
layer1_do = tf.keras.layers.Dropout(0.2)(pooled_output)
layer2 = tf.keras.layers.Dense(128, activation='swish')(layer1_do)
#layer2_bn = tf.keras.layers.BatchNormalization()(layer2)
layer2_do = tf.keras.layers.Dropout(0.2)(layer2)
layer3 = tf.keras.layers.Dense(256, activation='swish')(layer2_do)
layer3_do = tf.keras.layers.Dropout(0.2)(layer3)
layer4 = tf.keras.layers.Dense(128, activation='swish')(layer3_do)
layer4_do = tf.keras.layers.Dropout(0.2)(layer4)
layer5 = tf.keras.layers.Dense(1, activation='sigmoid')(layer4_do)

# Use inputs and outputs to construct a final model
model = tf.keras.Model(inputs=[text_input], outputs=[layer5])

#Reference: https://stackoverflow.com/questions/47605558/importerror-failed-to-import-pydot-you-must-install-pydot-and-graphviz-for-py

METRICS = [
    tf.keras.metrics.BinaryAccuracy(name='accuracy'),
    tf.keras.metrics.Precision(name='precision'),
    tf.keras.metrics.Recall(name='recall')
]

adam = Adam(lr=0.000001)
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=METRICS)

model.fit(X_train, y_train, epochs=50, batch_size=1024, callbacks=[es])

model.evaluate(X_test, y_test)

y_predicted = model.predict(X_test)

email_df = pd.read_csv(masteremail)
email_df["urgency"] = y_predicted

#Save
email_df.to_csv(masteremail,index=False)