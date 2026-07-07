from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

connection = sqlite3.connect("application_tracker.db", check_same_thread=False)
cursor = connection.cursor()

# Creates application table if it doesn't already exist
def create_table():
    cursor.execute(
        """ CREATE TABLE If NOT EXISTS applications(
        id INTEGER PRIMARY KEY,
        company TEXT,
        job_title TEXT,
        location TEXT,
        job_link TEXT,
        date_applied TEXT,
        status TEXT
        follow_up_date TEXT
        notes TEXT
        )
        """
    )
    
    connection.commit()
create_table()

# Create Flask application
app = Flask(__name__)

# Home page route
@app.route("/")
def home():
    return render_template("index.html")



# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)
