from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = "contacts.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        db.commit()


@app.route("/")
def home():
    return render_template("welcome.html")



@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)", 
                       (name, email, phone))
        db.commit()
        return redirect(url_for("view_contacts"))

    return render_template("add.html")



@app.route("/view")
def view_contacts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    return render_template("view.html", contacts=contacts)



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        cursor.execute("UPDATE contacts SET name=?, email=?, phone=? WHERE id=?", 
                       (name, email, phone, id))
        db.commit()
        return redirect(url_for("view_contacts"))

    cursor.execute("SELECT * FROM contacts WHERE id=?", (id,))
    contact = cursor.fetchone()
    return render_template("edit.html", contact=contact)



@app.route("/delete/<int:id>")
def delete_contact(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (id,))
    db.commit()
    return redirect(url_for("view_contacts"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
