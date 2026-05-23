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
    status = db.Column(db.String(50), default='Zatwierdzona')

with app.app_context():
    #db.drop_all()
    db.create_all()
    if not Kategoria.query.first():
        db.session.add_all([
            Kategoria(id=1, nazwa="Fryzjer i Barber"),
            Kategoria(id=2, nazwa="Kosmetyka"),
            Kategoria(id=3, nazwa="Manicure i Pedicure"),
            Kategoria(id=4, nazwa="Masaż i Fizjoterapia"),
            Kategoria(id=5, nazwa="Medycyna Estetyczna"),
            Kategoria(id=6, nazwa="Trening Personalny")
        ])
        db.session.commit()
    if not Pracownik.query.first():
        pracownicy_startowi = [
            Pracownik(imie_nazwisko="Adam Nowak", ocena=4.8, kategoria_id=1),
            Pracownik(imie_nazwisko="Jan Kowalski", ocena=4.2, kategoria_id=1),
            Pracownik(imie_nazwisko="Anna Wiśniewska", ocena=4.9, kategoria_id=2),
            Pracownik(imie_nazwisko="Ewa Kaczmarek", ocena=4.5, kategoria_id=3),
            Pracownik(imie_nazwisko="Piotr Zieliński", ocena=5.0, kategoria_id=4),
            Pracownik(imie_nazwisko="Marta Lewandowska", ocena=4.7, kategoria_id=5),
            Pracownik(imie_nazwisko="Tomasz Wójcik", ocena=4.6, kategoria_id=6)
        ]
        db.session.add_all(pracownicy_startowi)
        db.session.commit()

@app.route('/')
def domyslna():
    return redirect(url_for('logowanie'))

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    error = None
    if request.method == 'POST':
        email = request.form.get('userEmail')
        haslo = request.form.get('userPassword')
        uzytkownik = Uzytkownik.query.filter_by(email=email, haslo=haslo).first()
        if uzytkownik:
            session['uzytkownik_id'] = uzytkownik.id
            return redirect(url_for('index'))
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
        if len(haslo) < 6:
            error = "Błąd: Hasło musi mieć minimum 6 znaków."
        elif haslo != request.form.get('userPasswordRepeat'):
            error = "Błąd: Podane hasła nie są identyczne."
        elif Uzytkownik.query.filter_by(email=email).first():
            error = "Błąd: Użytkownik o podanym adresie e-mail już istnieje!"
        if error is None:
            nowy = Uzytkownik(imie_nazwisko=f"{imie} {nazwisko}", email=email, haslo=haslo, telefon=telefon, rola='klient')
            db.session.add(nowy)
            db.session.commit()
            return redirect(url_for('logowanie'))
    return render_template('rejestracja.html', error=error)

@app.route('/index')
def index():
    if 'uzytkownik_id' not in session:
        return redirect(url_for('logowanie'))
    kategorie = Kategoria.query.all()
    return render_template('index.html', kategorie=kategorie)

@app.route('/wybierz_date/<int:kategoria_id>')
def wybierz_date(kategoria_id):
    if 'uzytkownik_id' not in session: return redirect(url_for('logowanie'))
    kategoria = Kategoria.query.get_or_404(kategoria_id)
    return render_template('wybierz_date.html', kategoria=kategoria)

@app.route('/sprawdz_dostepnosc/<int:kategoria_id>', methods=['POST'])
def sprawdz_dostepnosc(kategoria_id):
    if 'uzytkownik_id' not in session: return redirect(url_for('logowanie'))
    wybrana_data_str = request.form.get('data_wizyty')
    wybrana_data = datetime.strptime(wybrana_data_str, '%Y-%m-%dT%H:%M')
    pracownicy = Pracownik.query.filter_by(kategoria_id=kategoria_id).all()
    lista_dostepnosci = []
    for p in pracownicy:
        zajety = Rezerwacja.query.filter_by(pracownik_id=p.id, data_wizyty=wybrana_data).first()
        lista_dostepnosci.append({'pracownik': p, 'dostepny': not zajety})
    kategoria = Kategoria.query.get(kategoria_id)
    return render_template('lista_pracownikow.html', pracownicy_status=lista_dostepnosci, kategoria=kategoria, wybrana_data=wybrana_data_str)

@app.route('/rezerwuj', methods=['POST'])
def rezerwuj():
    if 'uzytkownik_id' not in session: return redirect(url_for('logowanie'))
    pracownik_id = request.form.get('pracownik_id')
    data_str = request.form.get('data_wizyty')
    data_wizyty = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
    zajety = Rezerwacja.query.filter_by(pracownik_id=pracownik_id, data_wizyty=data_wizyty).first()
    if zajety:
        return "Błąd: Ten termin został już zajęty przez kogoś innego w międzyczasie."
    nowa_rezerwacja = Rezerwacja(uzytkownik_id=session['uzytkownik_id'], pracownik_id=pracownik_id, data_wizyty=data_wizyty)
    db.session.add(nowa_rezerwacja)
    db.session.commit()
    return "<script>alert('Zarezerwowano wizytę!'); window.location.href='/index';</script>"

@app.route('/wyloguj')
def wyloguj():
    session.clear()
    return redirect(url_for('logowanie'))

if __name__ == '__main__':
    app.run(debug=True)