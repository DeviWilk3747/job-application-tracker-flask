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

    # URL Values

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = ("SELECT * FROM applications")
    conditions = []
    parameters = []

    if search:
        # Searches and displays applications entered
        conditions.append("(company LIKE ? OR job_title LIKE ?)")
        parameters.append(f"%{search}%")
        parameters.append(f"%{search}%")

    if status:
        # Displays applications based on status selected
        conditions.append("status = ?")
        parameters.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    applications = cursor.fetchall()

    return render_template("view_applications.html", applications=applications, search=search, status=status)

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

@app.route("/edit-application/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    # Retrieves submitted data
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        job_title = request.form.get("job_title", "").strip()
        location = request.form.get("location", "").strip()
        job_link = request.form.get("job_link", "").strip()
        date_applied = request.form.get("date_applied", "").strip()
        status = request.form.get("status", "").strip()
        follow_up_date = request.form.get("follow_up_date", "").strip()
        notes = request.form.get("notes", "").strip()

        # Stops if any required field is empty
        if not company or not job_title or not date_applied or not status:
            return render_template(
                "edit_application.html",
                error="Company, job title, date applied, and status are required.",
                application=(application_id, company, job_title, location, job_link, date_applied, status, follow_up_date, notes)
            )
        
        cursor.execute(
            """
            UPDATE applications
            SET
                company = ?,
                job_title = ?,
                location = ?,
                job_link = ?,
                date_applied = ?,
                status = ?,
                follow_up_date = ?,
                notes = ?
            WHERE id = ?
            """,
            (company, job_title, location, job_link, date_applied, status, follow_up_date, notes, application_id)
        )

        connection.commit()
        flash("Application updated successfully")
        return redirect(url_for("view_applications"))
    
    # A GET request retrieves the current application for the form
    if request.method == "GET":
        cursor.execute(
            """
            SELECT * FROM applications
            WHERE id = ?
            """,
            (application_id,)
        )

        application = cursor.fetchone()

        # Handles an ID that does not exist
        if application is None:
            return "Application not found", 404

    # Send selected application to edit form    
    return render_template("edit_application.html", application=application)

@app.route("/dashboard")
def dashboard():

    # Counts how many total rows are in the application table
    cursor.execute("SELECT COUNT(*) FROM applications")
    result = cursor.fetchone()
    total_applications = result[0]

    # Counts applications by status
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status = ?",
        ("Applied",)
    )
    result = cursor.fetchone()
    applied_count = result[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status = ?",
        ("Interviewing",)
    )
    result = cursor.fetchone()
    interviewing_count = result[0]
    
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status = ?",
        ("Rejected",)
    )
    result = cursor.fetchone()
    rejected_count = result[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status = ?",
        ("Offers",)
    )
    result = cursor.fetchone()
    offers_count = result[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE status = ?",
        ("Saved",)
    )
    result = cursor.fetchone()
    saved_count = result[0]

    return render_template(
        "dashboard.html",
        total_applications=total_applications,
        applied_count=applied_count,
        interviewing_count=interviewing_count,
        rejected_count=rejected_count,
        offers_count=offers_count,
        saved_count=saved_count
    )

# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)
