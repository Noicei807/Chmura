from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Połączenie z bazą RDS
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Admin123%21@chmura-baza.cliwkweeidej.eu-north-1.rds.amazonaws.com:3306/rezerwacje'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Użytkownika
class Uzytkownik(db.Model):
    __tablename__ = 'uzytkownicy'
    id = db.Column(db.Integer, primary_key=True)
    imie_nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    haslo = db.Column(db.String(255), nullable=False)
    telefon = db.Column(db.String(20))
    rola = db.Column(db.String(50))
    rezerwacje = db.relationship('Rezerwacja', backref='klient', lazy=True)

# Model Usługi
class Usluga(db.Model):
    __tablename__ = 'uslugi'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(100), nullable=False)
    czas_trwania_min = db.Column(db.Integer)
    cena = db.Column(db.Numeric(10, 2))
    rezerwacje = db.relationship('Rezerwacja', backref='usluga_info', lazy=True)

# Model Rezerwacji z kluczami obcymi
class Rezerwacja(db.Model):
    __tablename__ = 'rezerwacje'
    id = db.Column(db.Integer, primary_key=True)
    uzytkownik_id = db.Column(db.Integer, db.ForeignKey('uzytkownicy.id'), nullable=False)
    usluga_id = db.Column(db.Integer, db.ForeignKey('uslugi.id'), nullable=False)
    data_wizyty = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Oczekująca')

# Inicjalizacja bazy danych
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rezerwuj', methods=['POST'])
def rezerwuj():
    try:
        uzytkownik_id = request.form.get('uzytkownik_id')
        usluga_id = request.form.get('usluga_id')
        data_str = request.form.get('data_wizyty') # Format: YYYY-MM-DD HH:MM:SS
        
        data_wizyty = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
        
        nowa_rezerwacja = Rezerwacja(
            uzytkownik_id=uzytkownik_id, 
            usluga_id=usluga_id, 
            data_wizyty=data_wizyty
        )
        db.session.add(nowa_rezerwacja)
        db.session.commit()
        return f"Sukces! Rezerwacja zapisana w RDS."
    except Exception as e:
        return f"Wystąpił błąd: {e}"

if __name__ == '__main__':
    app.run(debug=True)
