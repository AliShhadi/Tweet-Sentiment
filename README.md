# Tweets-Sentiment-Flask-App
This app uses the Tensorflow model (provided) that allows to predict tweets sentiment.

This model should be served with Tensorflow Serving in a docker container.

####Install Docker### 

https://docs.docker.com/docker-for-windows/install/

###Pulling a serving image### 

docker pull tensorflow/serving

###Running a serving image###

docker run -p 8501:8501 --mount type=bind,source=path\to\saved_model,target=/models/tweets-sentiment -e MODEL_NAME=tweets-sentiment -t tensorflow/serving

###Run the created container from docker###


###Verify the serving container is running:###

http://localhost:8501/v1/models/tweets-sentiment

###Run the flask app###

python app.py