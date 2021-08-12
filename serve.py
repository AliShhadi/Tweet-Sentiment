import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import preprocess
import json
import requests

vocab_size = 40000
embedding_dim = 64 # should be the 4th root of the vocab_size
max_length = 20 # max length, I used the average tweets length + std
trunc_type='post'
padding_type='post'
oov_tok = "<OOV>"

data = pd.read_csv('archive/tweets_used_in_training.csv', encoding = "ISO-8859-1")
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(data['text'].values)


def get_sentiments(input_tweets):
    input_tweets_prep = [preprocess.process_tweet(tweet) for tweet in input_tweets]
    print('preprocessed_input_tweets', input_tweets_prep)
    sequences = tokenizer.texts_to_sequences(input_tweets_prep)
    print('sequences', sequences)
    padded = pad_sequences(sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    print('padded',padded)
    print('padded tolist', padded.tolist())
    
    data = json.dumps({"signature_name": "serving_default", "instances": padded.tolist()})
    headers = {"content-type": "application/json"}

    json_response = requests.post('http://localhost:8501/v1/models/tweets-sentiment:predict', data=data,
                                  headers=headers)
    print(json_response)
    predictions = json.loads(json_response.text)['predictions']

    return predictions
    