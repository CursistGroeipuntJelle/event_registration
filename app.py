from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'  # Gebruik je eigen SMTP-server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '769b5d001@smtp-brevo.com'
app.config['MAIL_PASSWORD'] = '94dMZ0QnDwma6Atg'
app.config['MAIL_DEFAULT_SENDER'] = 'jelle.van.hulle3@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)


# Zorg ervoor dat de database-initialisatie in de toepassingscontext wordt uitgevoerd
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    search_query = request.args.get('search')
    if search_query:
        participants = Participant.query.filter(
            Participant.name.contains(search_query) |
            Participant.email.contains(search_query)
        ).all()
    else:
        participants = Participant.query.all()
    return render_template('index.html', participants=participants)


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    email = request.form['email']
    new_participant = Participant(name=name, email=email)
    db.session.add(new_participant)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete(id):
    participant = Participant.query.get_or_404(id)
    db.session.delete(participant)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    participant = Participant.query.get_or_404(id)
    if request.method == 'POST':
        participant.name = request.form['name']
        participant.email = request.form['email']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', participant=participant)


@app.route('/random', methods=['GET', 'POST'])
def random_picker():
    participants = Participant.query.all()
    if not participants:
        return redirect(url_for('index'))

    if request.method == 'POST':
        participant_id = request.form['participant_id']
        participant = Participant.query.get(participant_id)
        send_email = 'send_email' in request.form
        email_subject = request.form['email_subject']
        email_body = request.form['email_body']

        if send_email:
            send_email_to_participant(participant, email_subject, email_body)

        return render_template('random.html', participant=participant)

    random_participant = random.choice(participants)
    return render_template('random.html', participant=random_participant)


@app.route('/send_email', methods=['GET', 'POST'])
def send_email_page():
    participants = Participant.query.all()
    if request.method == 'POST':
        participant_id = request.form['participant_id']
        participant = Participant.query.get(participant_id)
        email_subject = request.form['email_subject']
        email_body = request.form['email_body']

        send_email_to_participant(participant, email_subject, email_body)

        return redirect(url_for('index'))

    return render_template('send_email.html', participants=participants)


def send_email_to_participant(participant, subject, body):
    msg = Message(subject, recipients=[participant.email])
    msg.body = body
    mail.send(msg)


if __name__ == '__main__':
    app.run(debug=True)