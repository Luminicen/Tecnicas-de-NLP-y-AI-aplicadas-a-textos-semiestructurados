#!/usr/bin/env python3
"""
train_spam_classifier.py

Script para entrenar una red neuronal simple (Keras) que clasifica correos como ham o spam.
Requisitos:
    pip install pandas scikit-learn tensorflow
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.callbacks import EarlyStopping

df = pd.read_csv('emails.csv')
df = df.dropna(subset=['text', 'label'])
le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])  # ham->0, spam->1
tX = df['text'].values
y = df['label_enc'].values
X_train, X_test, y_train, y_test = train_test_split(tX, y, test_size=0.2, random_state=42)
max_words = 10000   
max_len = 100      
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq  = tokenizer.texts_to_sequences(X_test)
X_train_pad = pad_sequences(X_train_seq, maxlen=max_len)
X_test_pad  = pad_sequences(X_test_seq,  maxlen=max_len)


model = Sequential([
    Embedding(input_dim=max_words, output_dim=16, input_shape=(max_len,)),  # especificar input_shape
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()
es = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)
history = model.fit(
    X_train_pad,
    y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2,
    callbacks=[es]
)
loss, acc = model.evaluate(X_test_pad, y_test)
print(f"\nTest Loss: {loss:.4f}, Test Accuracy: {acc:.4f}")