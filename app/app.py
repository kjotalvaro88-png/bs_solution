from flask import Flask, render_template, request, redirect, session, url_for
from datetime import date, timedelta
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
            session['rol'] = user[3]
            if user[3] == 'administrador':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('portal_cliente'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session or session['rol'] != 'administrador':
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario=session['usuario'])

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'usuario' not in session or session['rol'] != 'administrador':
        return redirect(url_for('login'))
    mensaje = None
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        telefono = request.form['telefono']
        correo = request.form['correo']
        usuario_cliente = request.form['usuario_cliente']
        contrasena_cliente = request.form['contrasena_cliente']
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (%s, %s, 'cliente')",
                        (usuario_cliente, contrasena_cliente))
            usuario_id = cur.lastrowid
            cur.execute("INSERT INTO clientes (nombre, cedula, telefono, correo, usuario_id) VALUES (%s, %s, %s, %s, %s)",
                        (nombre, cedula, telefono, correo, usuario_id))
            db.commit()
            mensaje = '¡Cliente registrado exitosamente!'
        except Exception as e:
            error = 'Error: la cédula o usuario ya existe.'
    return render_template('clientes.html', mensaje=mensaje, error=error)

@app.route('/moto', methods=['GET', 'POST'])
def moto():
    if 'usuario' not in session or session['rol'] != 'administrador':
        return redirect(url_for('login'))
    mensaje = None
    error = None
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, nombre, cedula FROM clientes")
    clientes = cur.fetchall()
    if request.method == 'POST':
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        anio = request.form['anio']
        cliente_id = request.form['cliente_id']
        descripcion = request.form['descripcion']
        repuestos = request.form['repuestos']
        proximo = (date.today() + timedelta(days=90)).strftime('%Y-%m-%d')
        try:
            cur.execute("INSERT INTO motos (placa, marca, modelo, anio, cliente_id) VALUES (%s, %s, %s, %s, %s)",
                        (placa, marca, modelo, anio, cliente_id))
            moto_id = cur.lastrowid
            cur.execute("INSERT INTO mantenimientos (moto_id, fecha, descripcion, repuestos, proximo_mantenimiento) VALUES (%s, CURDATE(), %s, %s, %s)",
                        (moto_id, descripcion, repuestos, proximo))
            db.commit()
            mensaje = '¡Moto y mantenimiento registrados exitosamente!'
        except Exception as e:
            error = 'Error: la placa ya existe.'
    return render_template('moto.html', mensaje=mensaje, error=error, clientes=clientes)

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if 'usuario' not in session or session['rol'] != 'administrador':
        return redirect(url_for('login'))
    resultados = None
    if request.method == 'POST':
        placa = request.form['placa']
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT m.placa, m.marca, m.modelo, m.anio,
                   c.nombre, c.cedula, c.telefono,
                   mt.fecha, mt.descripcion, mt.repuestos, mt.proximo_mantenimiento
            FROM motos m
            JOIN clientes c ON m.cliente_id = c.id
            JOIN mantenimientos mt ON mt.moto_id = m.id
            WHERE m.placa = %s
        """, (placa,))
        resultados = cur.fetchall()
    return render_template('historial.html', resultados=resultados)

@app.route('/portal')
def portal_cliente():
    if 'usuario' not in session or session['rol'] != 'cliente':
        return redirect(url_for('login'))
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM usuarios WHERE usuario=%s", (session['usuario'],))
    user = cur.fetchone()
    cur.execute("SELECT id FROM clientes WHERE usuario_id=%s", (user[0],))
    cliente = cur.fetchone()
    resultados = []
    if cliente:
        cur.execute("""
            SELECT m.placa, m.marca, m.modelo, m.anio,
                   mt.fecha, mt.descripcion, mt.repuestos, mt.proximo_mantenimiento
            FROM motos m
            JOIN mantenimientos mt ON mt.moto_id = m.id
            WHERE m.cliente_id = %s
        """, (cliente[0],))
        resultados = cur.fetchall()
    return render_template('portal_cliente.html', usuario=session['usuario'], resultados=resultados)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
