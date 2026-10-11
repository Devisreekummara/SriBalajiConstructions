
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-demo-secret")

DATABASE = os.path.join(app.root_path, "construction.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


create_tables()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/projects")
def projects():
    connection = get_db()
    project_list = connection.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template("projects.html", projects=project_list)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, phone, email, service, message]):
            flash("Please fill in all fields.")
            return redirect(url_for("contact"))

        connection = get_db()
        connection.execute("""
            INSERT INTO enquiries (name, phone, email, service, message)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, service, message))
        connection.commit()
        connection.close()

        flash("Your enquiry has been submitted successfully!")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Demo credentials: change these before public deployment.
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))

        flash("Incorrect username or password.")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    connection = get_db()

    enquiry_list = connection.execute(
        "SELECT * FROM enquiries ORDER BY id DESC"
    ).fetchall()

    project_list = connection.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        enquiries=enquiry_list,
        projects=project_list
    )


@app.route("/add-project", methods=["POST"])
def add_project():
    if not session.get("admin"):
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "Planning")

    if name and description:
        connection = get_db()
        connection.execute("""
            INSERT INTO projects (name, description, status)
            VALUES (?, ?, ?)
        """, (name, description, status))
        connection.commit()
        connection.close()

        flash("Project added successfully.")

    return redirect(url_for("dashboard"))



print("RUNNING SRI BALAJI WEBSITE")
print("PROJECT PATH:", os.path.abspath(__file__))

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
