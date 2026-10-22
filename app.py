
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_venue TEXT NOT NULL,
            event_description TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/events")
def events():
    connection = get_db_connection()
    all_events = connection.execute(
        "SELECT * FROM events ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template("events.html", events=all_events)


@app.route("/add-event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        event_venue = request.form["event_venue"]
        event_description = request.form["event_description"]

        connection = get_db_connection()
        connection.execute(
            """INSERT INTO events
            (event_name, event_date, event_venue, event_description)
            VALUES (?, ?, ?, ?)""",
            (event_name, event_date, event_venue, event_description)
        )
        connection.commit()
        connection.close()

        return redirect(url_for("events"))

    return render_template("add_event.html")


@app.route("/edit-event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    connection = get_db_connection()
    event = connection.execute(
        "SELECT * FROM events WHERE id = ?", (event_id,)
    ).fetchone()

    if event is None:
        connection.close()
        return "Event not found", 404

    if request.method == "POST":
        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        event_venue = request.form["event_venue"]
        event_description = request.form["event_description"]

        connection.execute(
            """UPDATE events
            SET event_name = ?, event_date = ?,
                event_venue = ?, event_description = ?
            WHERE id = ?""",
            (event_name, event_date, event_venue,
             event_description, event_id)
        )
        connection.commit()
        connection.close()

        return redirect(url_for("events"))

    connection.close()
    return render_template("edit_event.html", event=event)


@app.route("/delete-event/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    connection = get_db_connection()
    connection.execute(
        "DELETE FROM events WHERE id = ?", (event_id,)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("events"))


@app.route("/registrations", methods=["GET", "POST"])
def registrations():
    connection = get_db_connection()

    if request.method == "POST":
        student_name = request.form["student_name"].strip()
        student_email = request.form["student_email"].strip()
        event_id = request.form["event_id"]

        event = connection.execute(
            "SELECT id FROM events WHERE id = ?", (event_id,)
        ).fetchone()

        if student_name and student_email and event:
            connection.execute(
                """INSERT INTO registrations
                (student_name, student_email, event_id)
                VALUES (?, ?, ?)""",
                (student_name, student_email, event_id)
            )
            connection.commit()

        connection.close()
        return redirect(url_for("registrations"))

    all_events = connection.execute(
        "SELECT * FROM events ORDER BY event_date"
    ).fetchall()

    all_registrations = connection.execute("""
        SELECT registrations.id,
               registrations.student_name,
               registrations.student_email,
               events.event_name,
               events.event_date
        FROM registrations
        JOIN events ON registrations.event_id = events.id
        ORDER BY registrations.id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "registrations.html",
        events=all_events,
        registrations=all_registrations
    )


@app.route("/delete-registration/<int:registration_id>", methods=["POST"])
def delete_registration(registration_id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM registrations WHERE id = ?",
        (registration_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("registrations"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
