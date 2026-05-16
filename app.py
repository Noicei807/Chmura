from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Admin123%21@chmura-baza.cliwkweeidej.eu-north-1.rds.amazonaws.com:3306/rezerwacje'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Uzytkownik(db.Model):
    __tablename__ = 'uzytkownicy'
    id = db.Column(db.Integer, primary_key=True)
    imie_nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    haslo = db.Column(db.String(255), nullable=False)
    telefon = db.Column(db.String(20))
    rola = db.Column(db.String(50), default='klient')
    rezerwacje = db.relationship('Rezerwacja', backref='klient', lazy=True)

class Kategoria(db.Model):
    __tablename__ = 'kategorie'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(100), nullable=False)
    pracownicy = db.relationship('Pracownik', backref='kategoria', lazy=True)

class Pracownik(db.Model):
    __tablename__ = 'pracownicy'
    id = db.Column(db.Integer, primary_key=True)
    imie_nazwisko = db.Column(db.String(100), nullable=False)
    ocena = db.Column(db.Numeric(3, 2), default=5.00)
    kategoria_id = db.Column(db.Integer, db.ForeignKey('kategorie.id'), nullable=False)
    rezerwacje = db.relationship('Rezerwacja', backref='pracownik', lazy=True)

class Rezerwacja(db.Model):
    __tablename__ = 'rezerwacje'
    id = db.Column(db.Integer, primary_key=True)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey('uzytkownicy.id'), nullable=False)
    pracownik_id = db.Column(db.Integer, db.ForeignKey('pracownicy.id'), nullable=False)
    data_wizyty = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Oczekująca')

with app.app_context():
    # RĘCZNY RESET: Odkomentuj linię poniżej TYLKO na pierwsze uruchomienie
    db.drop_all()
    db.create_all()
    
    if not Kategoria.query.first():
        db.session.add_all([
            Kategoria(id=1, nazwa="Fryzjer"),
            Kategoria(id=2, nazwa="Kosmetyczka")
        ])
        db.session.commit()
        
    if not Pracownik.query.first():
        db.session.add_all([
            Pracownik(id=1, imie_nazwisko="Andrzej Nowak", ocena=4.85, kategoria_id=1),
            Pracownik(id=2, imie_nazwisko="Janusz Kowalski", ocena=4.20, kategoria_id=1),
            Pracownik(id=3, imie_nazwisko="Anna Wiśniewska", ocena=4.90, kategoria_id=2),
            Pracownik(id=4, imie_nazwisko="Maria Wójcik", ocena=4.60, kategoria_id=2)
        ])
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rezerwuj', methods=['POST'])
def rezerwuj():
    try:
        imie_nazwisko = request.form.get('imie_nazwisko')
        pracownik_id = request.form.get('pracownik_id')
        data_str = request.form.get('data_wizyty')
        
        data_wizyty = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
        
        uzytkownik = Uzytkownik.query.filter_by(imie_nazwisko=imie_nazwisko).first()
        if not uzytkownik:
            tymczasowy_email = f"{imie_nazwisko.replace(' ', '').lower()}@brak.pl"
            uzytkownik = Uzytkownik(imie_nazwisko=imie_nazwisko, email=tymczasowy_email, haslo="brak")
            db.session.add(uzytkownik)
            db.session.commit()

        nowa_rezerwacja = Rezerwacja(
            uzytkownik_id=uzytkownik.id, 
            pracownik_id=pracownik_id, 
            data_wizyty=data_wizyty
        )
        db.session.add(nowa_rezerwacja)
        db.session.commit()
        return f"Sukces! Rezerwacja u pracownika o ID {pracownik_id} zapisana."
    except Exception as e:
        return f"Wystąpił błąd: {e}"

if __name__ == '__main__':
    app.run(debug=True)
