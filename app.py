from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import pyrebase

config = {
    "apiKey": "AIzaSyBdboJz5Xoi30JyDT1pqxUJnCqWiyXKVIQ",
    "authDomain": "abstractivetextsummarization.firebaseapp.com",
    "databaseURL": "https://abstractivetextsummarization-default-rtdb.firebaseio.com",
    "projectId": "abstractivetextsummarization",
    "storageBucket": "bstractivetextsummarization.appspot.com",
    "messagingSenderId": "985957501888",
    "appId": "1:985957501888:web:8fcfb59e63ba7c72c35625",
    "measurementId": "G-B336RKSZK7",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

app = Flask(__name__)
app.secret_key = "your_secret_key"


# Login required to access any page
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

# Home Page 
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

#Sign Up
@app.route("/sign-up", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("sign.html")
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            auth.create_user_with_email_and_password(email, password)

            data = {"first_name": first_name, "last_name": last_name, "email": email}
            db.child("users").push(data)

            return redirect(url_for("/abstractive-summarization"))
        except:
            message = "Email Already Exists"
            return render_template("sign.html", message=message)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        try:
            auth.sign_in_with_email_and_password(email, password)

            session["user"] = email

            return redirect(url_for("abstractive_summarization"))
        except:
            message = "Invalid Email or Password"
            return render_template("login.html", message=message)
        
# Reset
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "GET":
        return render_template("reset.html")
    else:
        email = request.form["email"]
        try:
            auth.send_password_reset_email(email)
            message = "An email to reset the password has been successfully sent"
            return render_template("reset.html", message=message)
        except:
            message = "Something went wrong. Please check if the email you provided is registered or not."
            return render_template("reset.html", message=message)

# Abstractive Summarization
@app.route("/abstractive-summarization", methods=["GET", "POST"])
@login_required
def abstractive_summarization():
    return render_template("summarization.html")  

# Model
import requests

url = "https://1fe8-34-106-232-23.ngrok-free.app/summarization"

@app.route('/get_summarized_data', methods=['POST'])
def get_summarized_data():
    input = request.form['input']
    percentage = request.form['percentage']
    payload = {"input": input, "percentage": percentage}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        output = response.json()["output"]
        return jsonify({'summarized_text': output})
    else:
        print("Error:", response.text)


if __name__ == "__main__":
    app.run(debug=True)