from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rezerwuj', methods=['POST'])
def rezerwuj():
    imie = request.form.get('imie')
    usluga = request.form.get('usluga')
    
    # Pozniej bedzie dodany kod zapisujacy dane do bazy AWS RDS
    return f"{imie}, rezerwacja na usluge: {usluga} została wstepnie przyjeta!"

if __name__ == '__main__':
    app.run(debug=True)
