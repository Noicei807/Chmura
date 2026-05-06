from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# TWOJE HASLO ZAWSZE Z %21 ZAMIAST WYKRZYKNIKA
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Admin123%21@chmura-baza.cliwkweeidej.eu-north-1.rds.amazonaws.com:3306/rezerwacje'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Rezerwacja(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    usluga = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rezerwuj', methods=['POST'])
def rezerwuj():
    imie = request.form.get('imie')
    usluga = request.form.get('usluga')
    nowa_rezerwacja = Rezerwacja(imie=imie, usluga=usluga)
    db.session.add(nowa_rezerwacja)
    db.session.commit()
    return f"{imie}, rezerwacja na usluge: {usluga} została pomyślnie zapisana w chmurze AWS RDS!"

if __name__ == '__main__':
    app.run(debug=True)
