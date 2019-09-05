## model setting
max_features = 20000 # top 10000 words
maxlen = 200 # #of words per document
embedding_dim = 32

y = [1 if x == 'Buy' else 0 for x in df['comment']]
texts = df['text'][list([i for i in range(len(df)) if y[i]==1])].astype(str)
#texts = df['text'].astype(str)
tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
X = sequence.pad_sequences(sequences, maxlen=maxlen)

## Word Embedding
embedded_model = Sequential()
embedded_model.add(Embedding(max_features, embedding_dim, input_length=maxlen))
embedded_model.add(Flatten())
#embedded_model.add(Dense(32, activation='tanh'))
embedded_model.add(Dense(2, activation='tanh'))
embedded_model.compile('adam', 'mae')
#embedded_model.summary()
#X_embedded = embedded_model.predict(X)
X_embedded_Buy = embedded_model.predict(X)


###
plt.figure(figsize=(6, 6))
plt.scatter(X_embedded_Buy[:,0], X_embedded_Buy[:,1], c='blue')
plt.scatter(X_embedded_Sell[:,0], X_embedded_Sell[:,1], c='red')
#plt.colorbar()
plt.show()