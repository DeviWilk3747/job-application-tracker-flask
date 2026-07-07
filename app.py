from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

connection = sqlite3.connect("application_tracker.db", check_same_thread=False)
cursor = connection.cursor()

# Creates application table if it doesn't already exist
def create_table():
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY,
        company TEXT,
        job_title TEXT,
        location TEXT,
        job_link TEXT, 
        date_applied TEXT,
        status TEXT,
        follow_up_date TEXT,
        notes TEXT
        )
        """
    )
    
    connection.commit()
create_table()

# Create Flask application
app = Flask(__name__)

app.secret_key = "development-secret-key"

# Home page route
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add-application", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":

        # Retrieve submitted form data
        company = request.form.get("company", "").strip()
        job_title = request.form.get("job_title", "").strip()
        location = request.form.get("location", "").strip()
        job_link = request.form.get("job_link", "").strip()
        date_applied = request.form.get("date_applied", "").strip()
        status = request.form.get("status", "").strip()
        follow_up_date = request.form.get("follow_up_date", "").strip()
        notes = request.form.get("notes", "").strip()

        if not company or not job_title or not date_applied or not status:
            return render_template(
                "add_application.html",
                error="All fields required."
            )

        cursor.execute(
            """
            INSERT INTO applications
            (company, job_title, location, job_link, date_applied, status, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company, job_title, location, job_link, date_applied, status, follow_up_date, notes)
        )

        connection.commit()

        flash("Application added successfully!")
        return redirect(url_for("view_applications"))

    return render_template("add_application.html")
    
@app.route("/view-applications")
def view_applications():
    cursor.execute("""SELECT * FROM applications""")

    applications = cursor.fetchall()

    return render_template("view_applications.html", applications=applications)

@app.route("/delete-application/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    cursor.execute(
        """
        DELETE FROM applications
        WHERE id = ?
        """,
        (application_id,)
    )
    connection.commit()

    flash("Application deleted successfully.")
    return redirect(url_for("view_applications"))

# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)
