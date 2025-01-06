from flask import Flask, Blueprint, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance without passing the app
db = SQLAlchemy()

# Create the Blueprint
contact = Blueprint('contact', __name__, template_folder='templates')

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    msg = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, msg):
        self.name = name
        self.email = email
        self.msg = msg

# Define routes
@contact.route('/contact', methods=['GET', 'POST'])
def contact_page():
    message = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        msg = request.form['message']  # Changed to match form field name

        new_contact = Contact(name=name, email=email, msg=msg)  # Changed to match model field
        db.session.add(new_contact)
        db.session.commit()

        message = "Message sent successfully!"

    return render_template('contact.html', message=message)