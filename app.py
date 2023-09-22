from flask import Flask, render_template, request, redirect, session, url_for, flash
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson import ObjectId 

app = Flask(__name__)
app.secret_key = "05da2544-54c7-11ee-8c99-0242ac120002"
client = MongoClient("mongodb+srv://avisator:ES1BkGcjKXCZ5qTd@constiguide.bg2up9x.mongodb.net/")
db = client["Users"]
collection = db["users"]
count = db["count"] 
bcrypt = Bcrypt(app)


@app.route("/")
def home():
    username = None  
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]  
    return render_template('index.html', nav1=True, title="ConstiGuide", username=username)

@app.route("/info")
def information():
    username = None
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"] 
    return render_template('info.html', nav2=True, title="Constitution Information", username=username)

@app.route("/report")
def report():
    username = None
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"] 
    count_doc = count.find_one({})

    if count_doc:
        fully_know_count = int(count_doc["fullyknow"])
        to_some_extent_count = int(count_doc["extent"])
        dont_know_count = int(count_doc["dont"])
    else:
        fully_know_count = 0
        to_some_extent_count = 0
        dont_know_count = 0

    # Calculate the total number of responses
    total_responses = fully_know_count + to_some_extent_count + dont_know_count

    # Calculate percentages
    fully_know_percentage = (fully_know_count / total_responses) * 100
    to_some_extent_percentage = (to_some_extent_count / total_responses) * 100
    dont_know_percentage = (dont_know_count / total_responses) * 100

    return render_template(
        'report.html',
        fully_know_percentage=fully_know_percentage,
        to_some_extent_percentage=to_some_extent_percentage,
        dont_know_percentage=dont_know_percentage, nav3=True,
        fully_know_count=fully_know_count,
        to_some_extent_count=to_some_extent_count,
        dont_know_count=dont_know_count, username=username  # Pass these variables to the template
    )


@app.route("/credits")
def credits():
    username = None  #
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]  
    return render_template('credits.html', nav4=True, username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = collection.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
    
            session["user_id"] = str(user["_id"])
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login failed. Please check your username and password.", "danger")

    return render_template('login.html', nav5=True)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        admin = 'False'
        
        if collection.find_one({"username": username}):
            return 'This username is being used'
        
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")


        user = {"username": username, "password": hashed_password, "admin": admin}
        collection.insert_one(user)
        return redirect(url_for("login"))
    return render_template('register.html', nav6=True)

@app.route("/admin")
def admin():
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user and user["admin"] == "True":
            users = collection.find()
            return render_template('admin.html', nav8=True, users=users)
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logout successful!", "success")
    return redirect(url_for("home"))


@app.route("/quiz")
def quiz():
    username = None  
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]  
    return render_template('quiz.html', nav7=True, username=username)

@app.route("/vote", methods=["GET", "POST"])
def vote():
    username = None
    if "user_id" in session:
        user = collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            username = user["username"]

    if "user_id" in session:
        # Check if the user has already voted
        if user.get("voted", False):
            flash("You have already voted. You cannot access this page again.", "danger")
            return redirect(url_for("home"))  # Redirect to another page (e.g., home page)

        if request.method == 'POST':
            knowledge = request.form['knowledge']

            # Get the current user's ID
            user_id = ObjectId(session["user_id"])

            # Update the user's document to indicate that they have voted
            collection.update_one({"_id": user_id}, {"$set": {"voted": True}})

            # Get the current values from the count document
            count_doc = count.find_one({})

            if count_doc:
                fullyknow = int(count_doc["fullyknow"])
                extent = int(count_doc["extent"])
                dont = int(count_doc["dont"])

                if knowledge == 'know':
                    fullyknow += 1
                elif knowledge == 'extent':
                    extent += 1
                elif knowledge == 'dont-know':
                    dont += 1

                # Update the values in the count document
                count.update_one({}, {"$set": {"fullyknow": str(fullyknow), "extent": str(extent), "dont": str(dont)}})
                flash("Knowledge updated, and your vote has been recorded!", "success")

        return render_template('vote.html', nav3=True, username=username)
    return redirect(url_for("register"))





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
