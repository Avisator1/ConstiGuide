from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html', nav1=True, title="ConstiGuide")

@app.route("/info")
def information():
    return render_template('info.html', nav2=True, title="Constitution Information")

@app.route("/report")
def report():
    return render_template('report.html', nav3=True, title="Poll Report")

@app.route("/credits")
def credits():
    return render_template('credits.html', nav4=True)

@app.route("/login")
def login():
    return render_template('login.html', nav5=True)

@app.route("/register")
def register():
    return render_template('register.html', nav6=True)

@app.route("/quiz")
def quiz():
    return render_template('quiz.html', nav7=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0' , debug=True)