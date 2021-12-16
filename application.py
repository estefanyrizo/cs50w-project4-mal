import os
from re import A
import re

import requests
from dotenv import load_dotenv
from flask import Flask, json, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, flash, redirect, render_template, request, session
from sqlalchemy.sql.elements import Null
from tempfile import mkdtemp
from sqlalchemy.sql.expression import select
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, administrador
from flask import jsonify

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def busqueda():
    q = request.args.get("q")
    rit_id = request.args.get('rit_id', type = int)
    print(q)
    if q and not rit_id:
        coreografias = db.execute(f"SELECT c.id, titulo, descripcion, portada, co.nombre AS coreografo, ri.nombre AS ritmo from coreografos AS co INNER JOIN coreografias as c ON (coreografo_id = co.id) INNER JOIN ritmos as ri on (ritmo_id = ri.id) WHERE c.estado = true AND (UPPER(co.nombre) LIKE UPPER('%{q}%') OR UPPER(c.titulo) LIKE UPPER('%{q}%') OR UPPER(ri.nombre) LIKE UPPER('%{q}%')) LIMIT 5")
        if not coreografias.fetchone():
            flash(f"No encontre la coreografia {q}:c","error")
            return redirect("/")
        data = []
        for coreo in coreografias:
            data.append(dict(coreo))
        return jsonify(data)

    elif rit_id and not q:
        coreografias = db.execute(f"SELECT * FROM coreografias WHERE estado = true")
        data = []
        for coreo in coreografias:
            data.append(dict(coreo))
        return jsonify(data)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registrar usuario"""
    session.clear()

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":

        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return flash("Campos incompletos", "error")

        if not request.form.get("password") == request.form.get("confirmation"):
            flash("Las contraseñas no coinciden", "error")
            return render_template("register.html")

        if db.execute(f"SELECT * FROM users WHERE username = '{request.form.get('username')}'").rowcount > 0:
            flash("El usuario ya existe :(", "error")
            return render_template("register.html")

        else:
            password = generate_password_hash(request.form.get("password"))
            db.execute(f"INSERT INTO users (nombre,username, hash, isAdmin) VALUES ('{request.form.get('nombre')}', '{request.form.get('username')}', '{password}', false)")
            db.commit()

            user = db.execute(f"SELECT id, isAdmin FROM users WHERE username= '{request.form.get('username')}'").fetchone()

            # Remember which user has logged in
            session["user_id"] = user["id"]
            session["admin"] = user["isadmin"]

            flash("Registrado!", "exito") 
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username") or not request.form.get("password"):
            return flash("Campos incompletos", "error")
        
        query = db.execute(f"select * from users WHERE username = '{request.form.get('username')}'").fetchone()

        if not query or not check_password_hash(query['hash'], request.form.get("password")):
            flash("Nombre o contraseña incorrectos", "error")
            return render_template("login.html")

        session["user_id"] = query['id']
        session["admin"] = query["isadmin"]
        session["perfil"] = query["perfil"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect("/")

@app.route("/micuenta", methods=["GET", "POST"])
@login_required
def micuenta():
    usuario = db.execute(f"SELECT * FROM users WHERE id = {session['user_id']}")
    if request.method == "GET":
        return render_template("micuenta.html", usuario = usuario)

    elif request.method == "POST":
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        biografia = request.form.get('biografia')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        
        foto = request.form.get("perfil")

        if correo:
            db.execute(f"UPDATE users SET correo = '{correo}' WHERE id = {session['user_id']}")
        
        if telefono:
            db.execute(f"UPDATE users SET telefono = '{telefono}' WHERE id = {session['user_id']}")
        
        if biografia: 
            db.execute(f"UPDATE users SET biografia = '{biografia}' WHERE id = {session['user_id']}")

        if nombre:
            db.execute(f"UPDATE users SET nombre = '{nombre}' WHERE id = {session['user_id']}")
        
        if apellido:
            db.execute(f"UPDATE users SET apellido = '{apellido}' WHERE id = {session['user_id']}")

        if foto:
            db.execute(f"UPDATE users SET perfil = '{foto}' WHERE id = {session['user_id']}")
            session["perfil"] = foto

        db.commit()     
                
        flash("Cambios realizados", "exito")
        return redirect("/micuenta")

@app.route("/actualizarcontraseña", methods=["GET", "POST"])
@login_required
def cambiarcontraseña():
    if request.method == "GET":
        return render_template("actualizarcontraseña.html")

    elif request.method == "POST":
        lastpassword = request.form.get("last_password")
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")

        rows = db.execute(f"SELECT hash from users where id = {session['user_id']}").fetchone()

        print(newpassword)
        print(confirmation)

        if not check_password_hash(rows['hash'], lastpassword):
            flash("Contraseña anterior incorrecta", "error")
            return render_template("actualizarContraseña.html")

        # Validar que password y confirmation tengan los mismos valores
        if newpassword != confirmation:
            flash("Las contraseñas no coindicen", "error")
            return render_template("actualizarcontraseña.html")

        elif check_password_hash(rows['hash'], newpassword):
            flash("La nueva contraseña no puede ser igual a la anterior", "error")
            return render_template("actualizarContraseña.html") 

        # Ingresar los datos a la base de datos
        else:
            password = generate_password_hash(newpassword)
            db.execute(f"UPDATE users SET hash = '{password}' WHERE id = {session['user_id']}")
            db.commit()
            flash("Contraseña actualizada", "exito")

            # Redireccionar al index
            return redirect("/")

@app.route("/registrar", methods=["GET", "POST"])
@login_required
@administrador
def registrar():
    """Registrar usuario Admin"""

    if request.method == "GET":
        return render_template("registrar.html")

    elif request.method == "POST":

        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return flash("Campos incompletos", "error")

        if not request.form.get("password") == request.form.get("confirmation"):
            flash("Las contraseñas no coinciden", "error")
            return render_template("register.html")

        if db.execute(f"SELECT * FROM users WHERE username = '{request.form.get('username')}'").rowcount > 0:
            flash("El usuario ya existe :(", "error")
            return render_template("register.html")

        else:
            password = generate_password_hash(request.form.get("password"))
            db.execute(f"INSERT INTO users(nombre, username, hash, isAdmin) VALUES ('{request.form.get('nombre')}', '{request.form.get('username')}', '{password}', true)")
            db.commit()

            flash("Registrado!", "exito") 
            return redirect("/")

@app.route("/subir-coreografia", methods=["GET", "POST"])           
@login_required
def subirCoreo():
    """Subir contenido de coreografias"""
    ritmos = db.execute("SELECT * FROM ritmos")
    coreografos = db.execute("SELECT * FROM coreografos limit 20")
    if request.method == "POST":

        if not request.form.get("titulo") or not request.form.get("descripcion") or not request.form.get("ritmo") or not request.form.get("url") or not request.form.get("urlV"):
            flash(f"Campos incompletos {request.form.get('url')}, {request.form.get('urlV')}", "error")
            return render_template("subir-coreografia.html", ritmos = ritmos)
        
        estado = False
        
        if session["admin"] == True:
            estado = True

        if request.form.get("coreografo"):
            coreografo = request.form.get("coreografo")

        elif request.form.get("nombre") and request.form.get("nacionalidad"):
            db.execute(f"INSERT INTO coreografos (nombre, nacionalidad) VALUES ('{request.form.get('nombre')}', '{request.form.get('nacionalidad')}')")
            db.commit()
            coreografo = db.execute(f"SELECT id from coreografos WHERE nombre = '{request.form.get('nombre')}'").fetchone()["id"]

        db.execute(f"INSERT INTO coreografias (titulo, descripcion, portada, estado, ritmo_id, coreografo_id, user_id) VALUES ('{request.form.get('titulo')}', '{request.form.get('descripcion')}', '{request.form.get('url')}', {estado}, {request.form.get('ritmo')}, {coreografo}, {session['user_id']})")
        db.commit()
        idCoreo = db.execute(f"SELECT id FROM coreografias WHERE titulo = '{request.form.get('titulo')}'").fetchone()

        db.execute(f"INSERT INTO videos (enlace, coreo_id) VALUES ('{request.form.get('urlV')}', {idCoreo['id']})")
        db.commit()
        flash("Agregado correctamente", "exito")
        return redirect("/")
    else:
        return render_template("subir-coreografia.html", ritmos = ritmos, coreografos = coreografos)
        
@app.route("/coreografia/<id>", methods=["GET", "POST"])
@login_required
def coreografia(id):

    coreo = db.execute(f"SELECT c.id, c.titulo, c.descripcion, c.portada, c.estado, v.enlace, co.nombre as coreografo, co.nacionalidad FROM videos v INNER JOIN coreografias c ON (v.coreo_id =  c.id) INNER JOIN coreografos co ON(c.coreografo_id = co.id) WHERE v.coreo_id =  {id}").fetchone()

    if coreo and coreo["estado"] == True:

        if request.method == "GET":

            comentarios = db.execute(f"SELECT comentario, username FROM comentarios AS c INNER JOIN users AS u ON c.user_id = u.id WHERE c.coreo_id = {id} limit 5")
            likes = db.execute(f"SELECT * FROM likes WHERE coreo_id = {id} and me_gusta = true").rowcount
            me_gusta = db.execute(f"SELECT * FROM likes WHERE coreo_id = {id} and me_gusta = true AND user_id = {session['user_id']}").fetchone()
            return render_template("coreo.html", coreo = coreo, comentarios=comentarios, likes=likes, me_guta = me_gusta)

        else:
        
            db.execute(f"INSERT INTO comentarios (coreo_id, comentario, user_id) VALUES ({id}, '{request.form.get('comentario')}', {session['user_id']})")
            db.commit()

            return redirect(f"{id}")

    else:
        flash("Perdón, no encontré la coreografia, busca otra :c", "error")
        return redirect("/")

@app.route("/likes")
@login_required
def likes():
    id = request.args.get("id")
    likes = db.execute(f"SELECT * FROM likes WHERE coreo_id = {id} and me_gusta = true").rowcount
    me_gusta = db.execute(f"SELECT me_gusta FROM likes WHERE coreo_id = {id} AND user_id = {session['user_id']}").fetchone()
    if not me_gusta:
        db.execute(f"INSERT INTO likes(coreo_id, user_id, me_gusta) VALUES ({id}, {session['user_id']}, true)")
        db.commit()
        me_gusta = {"me_gusta" : True}
    elif me_gusta["me_gusta"] == True:
        db.execute(f"DELETE from likes WHERE user_id = {session['user_id']}")
        db.commit()
        me_gusta = {"me_gusta" : False}

    return {"id": id, "likes": likes, "me_gusta": me_gusta["me_gusta"]}

@app.route("/revision", methods=["GET"])
@administrador
@login_required
def revision():
    coreos = db.execute("SELECT c.id, titulo, descripcion, portada, co.nombre AS coreografo from coreografos AS co INNER JOIN coreografias as c ON coreografo_id = co.id WHERE c.estado = false")
    return render_template("revision.html", coreos = coreos)

@app.route("/mis-coreografias", methods=["GET"])
@login_required
def misCoreos():
    coreos = db.execute(f"SELECT c.id, titulo, descripcion, portada, estado, co.nombre AS coreografo from coreografos AS co INNER JOIN coreografias as c ON coreografo_id = co.id WHERE user_id = {session['user_id']}")
    return render_template("mis-coreos.html", coreos = coreos)

@app.route("/aprobado", methods=["GET"])
@login_required
def aprobado():
        id = request.args.get("id")
        db.execute(f"UPDATE coreografias SET estado = true WHERE id = {id}")
        db.commit()
        flash("La coreografia ya se encuentra visible en la pagina", "exito")
        return redirect("/")
    
@app.route("/eliminado", methods=["GET"])
@login_required
def eliminado():
        id = request.args.get("id")
        db.execute(f"DELETE FROM videos WHERE coreo_id = {id}")
        db.execute(f"DELETE FROM coreografias WHERE id = {id}")
        db.commit()
        flash("La coreografia ha sido eliminada", "triste")
        return redirect("/")

