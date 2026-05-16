from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_sekretny_klucz_do_sesji'
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
def domyslna():
    return redirect(url_for('logowanie'))

@app.route('/index')
def index():
    if 'uzytkownik_id' not in session:
        return redirect(url_for('logowanie'))
    return render_template('index.html')

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    error = None
    if request.method == 'POST':
        email = request.form.get('userEmail')
        haslo = request.form.get('userPassword')

        uzytkownik = Uzytkownik.query.filter_by(email=email, haslo=haslo).first()
        if uzytkownik:
            session['uzytkownik_id'] = uzytkownik.id
            session['rola'] = uzytkownik.rola
            return redirect(url_for('index'))
        else:
            error = "Niepoprawny adres e-mail lub hasło."

    return render_template('logowanie.html', error=error)

@app.route('/rejestracja', methods=['GET', 'POST'])
def rejestracja():
    error = None
    if request.method == 'POST':
        imie = request.form.get('userName')
        nazwisko = request.form.get('userSurname')
        email = request.form.get('userEmail')
        telefon = request.form.get('userNumber')
        haslo = request.form.get('userPassword')
        haslo_powtorz = request.form.get('userPasswordRepeat')

        if len(haslo) < 6:
            error = "Błąd: Hasło musi mieć minimum 6 znaków."
        elif haslo != haslo_powtorz:
            error = "Błąd: Podane hasła nie są identyczne."
        elif Uzytkownik.query.filter_by(email=email).first():
            error = "Błąd: Użytkownik o podanym adresie e-mail już istnieje!"

        if error is None:
            pelnosc_imie_nazwisko = f"{imie} {nazwisko}"
            nowy = Uzytkownik(
                imie_nazwisko=pelnosc_imie_nazwisko,
                email=email,
                haslo=haslo,
                telefon=telefon,
                rola='klient'
            )
            db.session.add(nowy)
            db.session.commit()
            return redirect(url_for('logowanie'))

    return render_template('rejestracja.html', error=error)

@app.route('/wyloguj')
def wyloguj():
    session.clear()
    return redirect(url_for('logowanie'))

if __name__ == '__main__':
    app.run(debug=True)
