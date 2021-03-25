"""Our single page Tweepy web application"""
from os import getenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from twitter import get_info, get_followers_avg_favorites
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB = SQLAlchemy(app)

# endpoint == "/"
@app.route("/")
def root():
    users = Users.query.all()
    return render_template("base.html", users=users)


# endpoint == "user_submitted"
@app.route("/user_submitted", methods=["POST"])
def user_submitted():
    username = request.values["username"]
    # dtypes: user = <user twitter objects>, user_tweets = <tweets>
    user, user_tweets = get_info(username)
    followers, avg_favorites = get_followers_avg_favorites(username)
    DB_user = Users(
        id=user.id, 
        username= user.screen_name, 
        fullname=user.name, 
        tweets = user_tweets,
        followers= followers,
        average_favorites=avg_favorites
    )
    DB.session.add(DB_user)
    DB.session.commit()
    return render_template("user.html", username=username, tweets=user_tweets)

# endpoint == "reset"
@app.route("/reset")
def reset():
    DB.drop_all()
    DB.create_all()
    return render_template("reset.html")

# endpoint == "predict"
@app.route("/predict")
def predict():
    return render_template("predict.html")

@app.route("/predictions", methods=["POST"])
def predictions():
# make model
    # Train a model with what is "currently" in Users
    # x will be number of followers
    # I'm predicting average number of favorites
    queried_data = Users.query.all()
    X_list = [user.followers for user in queried_data]
    X_train = np.array(X_list).reshape(-1, 1)
    y_train = [user.average_favorites for user in queried_data]
    rf_model = RandomForestRegressor(n_estimators=200, 
        criterion="mae",
        n_jobs=-1).fit(X_train, y_train)
# predict whoever's username is entered in /predict
    username = request.values["username"]
    followers, avg_favorites = get_followers_avg_favorites(username)
    X_test = np.array(followers).reshape(1, -1)
    prediction = rf_model.predict(X_test)
    y_true = [avg_favorites]
    model_score = mean_absolute_error(y_true, prediction)
    return render_template(
        "predictions.html", 
        username = username,
        avg_num_faves= round(prediction[0]),
        true_num= round(y_true[0]),
        score= round(model_score)
    )


# Creating a users database
class Users(DB.Model):
    """Stores Twitter users and corresponding tweets"""
    id = DB.Column(DB.BigInteger, primary_key = True)
    username = DB.Column(DB.String(50), nullable=False) 
    fullname = DB.Column(DB.String(50), nullable=False)
    tweets = DB.Column(DB.PickleType)
    followers = DB.Column(DB.Integer, nullable = False)
    average_favorites = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return "<User {}>".format(self.fullname)