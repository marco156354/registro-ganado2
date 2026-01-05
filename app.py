from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# -----------------------
# BASE DE DATOS
# -----------------------
def get_db():
    return sqlite3.connect("ganado.db")

def crear_tablas():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS nacimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        becerro TEXT,
        fecha TEXT,
        sexo TEXT,
        vaca TEXT,
        toro TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS cargas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vaca TEXT,
        fecha TEXT,
        toro TEXT
    )
    """)

    db.commit()
    db.close()

crear_tablas()

# -----------------------
# RUTAS
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nacimientos", methods=["GET", "POST"])
def nacimientos():
    if request.method == "POST":
        d = request.form
        db = get_db()
        db.execute(
            "INSERT INTO nacimientos (becerro, fecha, sexo, vaca, toro) VALUES (?, ?, ?, ?, ?)",
            (d["becerro"], d["fecha"], d["sexo"], d["vaca"], d["toro"])
        )
        db.commit()
        db.close()
        return redirect("/nacimientos")

    return render_template("nacimientos.html")

@app.route("/cargas", methods=["GET", "POST"])
def cargas():
    if request.method == "POST":
        d = request.form
        db = get_db()
        db.execute(
            "INSERT INTO cargas (vaca, fecha, toro) VALUES (?, ?, ?)",
            (d["vaca"], d["fecha"], d["toro"])
        )
        db.commit()
        db.close()
        return redirect("/cargas")

    return render_template("cargas.html")

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")

    db = get_db()
    c = db.cursor()

    nacimientos = c.execute(
        "SELECT * FROM nacimientos WHERE becerro LIKE ? OR vaca LIKE ? OR toro LIKE ?",
        (f"%{q}%", f"%{q}%", f"%{q}%")
    ).fetchall()

    cargas = c.execute(
        "SELECT * FROM cargas WHERE vaca LIKE ? OR toro LIKE ?",
        (f"%{q}%", f"%{q}%")
    ).fetchall()

    total_n = c.execute("SELECT COUNT(*) FROM nacimientos").fetchone()[0]
    total_c = c.execute("SELECT COUNT(*) FROM cargas").fetchone()[0]

    db.close()

    return render_template(
        "buscar.html",
        nacimientos=nacimientos,
        cargas=cargas,
        total_n=total_n,
        total_c=total_c,
        q=q
    )

# -----------------------
# ELIMINAR REGISTROS
# -----------------------
@app.route("/eliminar/<tipo>/<int:id>")
def eliminar(tipo, id):
    db = get_db()
    if tipo == "nacimiento":
        db.execute("DELETE FROM nacimientos WHERE id=?", (id,))
    elif tipo == "carga":
        db.execute("DELETE FROM cargas WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for("buscar"))

if __name__ == "__main__":
    app.run(debug=True)
