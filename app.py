from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "cheie_super_secreta"

# Configurare conexiune MySQL
db = mysql.connector.connect(
    host="localhost",
    user="phpmyadmin",
    password="sqrt666",
    database="flaskapp"
)
cursor = db.cursor()

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        username=session['user']
        #return f"Welcome, {session['user']}!"
        return render_template('dashboard.html', username=username)
    else:
        return redirect("/")
    #return render_template('dashboard.html', title='Web App Python Flask - Dashboard')

@app.route("/logout")
def logout():
    #session.pop("user", None)
    session.clear()
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[3]  # indexul depinde de ordinea coloanelor
            if check_password_hash(stored_password, password):
                session['user'] = user[1]  # username
                session['email'] = user[2]
                flash("Login successful!", "success")
                return redirect("/dashboard")
            else:
                flash("Wrong password", "danger")
        else:
            flash("User not found", "warning")

    return render_template("index.html")  # pagina de login


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        #salvare in DB
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        db.commit()
        return redirect("/")

    return render_template('register.html', title="Web App Python Flask - Register")

@app.route('/reset-pass', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect('/reset-pass')


        hashed_pw = generate_password_hash(new_password)
        email = session.get('email')
        if not email:
            flash("You're not logged in", "warning")
            return redirect('/')

        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_pw, email))
        db.commit()
        flash("Password reset successful. You can now log in.", "success")
        return redirect('/')

    return render_template('reset_pass.html', title="Reset Password")


if __name__ == "__main__":
	#app.run()
	app.run(host='127.0.0.1',port=5000,debug=True)
