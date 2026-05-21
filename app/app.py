from flask import Flask, render_template, request, redirect, session, url_for
import MySQLdb
import os

app = Flask(__name__)
app.secret_key = 'bssolution2026'

def get_db():
    return MySQLdb.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'bsuser'),
        passwd=os.environ.get('DB_PASSWORD', 'bs1234'),
        db=os.environ.get('DB_NAME', 'bs_solution')
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s", (usuario, contrasena))
        user = cur.fetchone()
        if user:
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario=session['usuario'])

@app.route('/moto', methods=['GET', 'POST'])
def moto():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    mensaje = None
    if request.method == 'POST':
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        anio = request.form['anio']
        descripcion = request.form['descripcion']
        repuestos = request.form['repuestos']
        proximo = request.form['proximo']
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO motos (placa, marca, modelo, anio) VALUES (%s, %s, %s, %s)",
                    (placa, marca, modelo, anio))
        moto_id = cur.lastrowid
        cur.execute("INSERT INTO mantenimientos (moto_id, fecha, descripcion, repuestos, proximo_mantenimiento) VALUES (%s, CURDATE(), %s, %s, %s)",
                    (moto_id, descripcion, repuestos, proximo))
        db.commit()
        mensaje = '¡Moto y mantenimiento registrados exitosamente!'
    return render_template('moto.html', mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
