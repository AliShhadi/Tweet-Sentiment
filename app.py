import json
import tweepy
import serve

from flask_cors import CORS
from requests_oauthlib import OAuth1Session
from flask import Flask, request, jsonify, render_template

consumer_key = "insert here your Twitter consumer_key (create new app in your Twitter developer account)"
consumer_secret = "insert here your Twitter consumer_secret"

# leave the following variables empty. They will be filled automatically.
access_token = ""
access_token_secret = ""

resource_owner_key = ""
resource_owner_secret = ""
oauth_verifier = ""
auth = ""
api = ""

app = Flask(__name__)

CORS(app)  # needed for cross-domain requests, allow everything by default


def get_resource_token():
    # create an object of OAuth1Session
    request_token = OAuth1Session(client_key=consumer_key, client_secret=consumer_secret)
    # twitter endpoint to get request token
    url = 'https://api.twitter.com/oauth/request_token'
    # get request_token_key, request_token_secret and other details
    data = request_token.get(url)
    # split the string to get relevant data
    data_token = str.split(data.text, '&')
    ro_key = str.split(data_token[0], '=')
    ro_secret = str.split(data_token[1], '=')
    global resource_owner_key
    global resource_owner_secret
    resource_owner_key = ro_key[1]
    resource_owner_secret = ro_secret[1]
    return None


def new_tab_to_authenticate():
    url = 'https://api.twitter.com/oauth/authenticate?oauth_token=' + resource_owner_key
    return url


def twitter_get_access_token():
    oauth_token = OAuth1Session(client_key=consumer_key,
                                client_secret=consumer_secret,
                                resource_owner_key=resource_owner_key,
                                resource_owner_secret=resource_owner_secret)
    url = 'https://api.twitter.com/oauth/access_token'
    data = {"oauth_verifier": oauth_verifier}
    access_token_data = oauth_token.post(url, data=data)
    access_token_list = str.split(access_token_data.text, '&')
    temp_ck = str.split(access_token_list[0], '=')
    temp_cks = str.split(access_token_list[1], '=')
    global access_token
    global access_token_secret
    access_token = temp_ck[1]
    access_token_secret = temp_cks[1]
    return access_token + "////" + access_token_secret


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/redirecting')
def redirecting():
    return render_template('redirecting.html')


@app.route('/redirect_and_sign_in', methods=['POST'])
def redirect_and_sign_in():
    get_resource_token()
    return new_tab_to_authenticate()


@app.route('/get_oauth_verifier', methods=['POST'])
def get_oauth_verifier():
    global oauth_verifier
    oauth_verifier = str(request.json)
    tokens = twitter_get_access_token()
    global auth
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    global api
    api = tweepy.API(auth)
    return tokens


@app.route('/get_keys_from_client', methods=['POST'])
def get_keys_from_client():
    param = [str(x) for x in request.json]
    global access_token
    global access_token_secret
    access_token = param[0]
    access_token_secret = param[1]
    global auth
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    global api
    api = tweepy.API(auth)
    return "success"


@app.route('/retrieve', methods=['POST'])
def retrieve():
    retrieved_tweets = []
    param = [str(x) for x in request.json]
    try:
        cursor = tweepy.Cursor(api.user_timeline, id=param[0], tweet_mode="extended").items(int(param[1]))
        for tweet in cursor:
            retrieved_tweets.append(str(tweet.created_at) + "DateAndTweetSeparatorForProject" + tweet.full_text +
                                    "DateAndTweetSeparatorForProject" + tweet.lang)
        return jsonify(retrieved_tweets)
    except tweepy.TweepError:
        retrieved_tweets.clear()
        retrieved_tweets.append("Check username or try again")
        return jsonify(retrieved_tweets)


@app.route('/predict', methods=['POST'])
def predict():
    # Create JSON Object
    input_tweets = [x["tweet"] for x in request.json]
    predictions = serve.get_sentiments(input_tweets)
    
    return jsonify(predictions)


if __name__ == "__main__":
    app.run(debug=True)
