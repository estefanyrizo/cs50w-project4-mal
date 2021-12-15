import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

# Carga las variables de entorno que tengo en .env
load_dotenv()

engine= create_engine(os.getenv("DATABASE_URL"))
db =scoped_session(sessionmaker(bind=engine))

""" ### Querys de creacion de las tablas
query_create_users = "CREATE TABLE users(id SERIAL PRIMARY KEY NOT NULL, username VARCHAR NOT NULL, hash VARCHAR NOT NULL, isAdmin BOOLEAN, correo VARCHAR, telefono INTEGER, biografia VARCHAR, nombre VARCHAR NOT NULL, apellido VARCHAR, perfil VARCHAR)"
query_create_coreagrafos = "CREATE TABLE coreografos(id SERIAL PRIMARY KEY NOT NULL, nombre VARCHAR NOT NULL, nacionalidad VARCHAR)"
query_create_ritmos = "CREATE TABLE ritmos(id SERIAL PRIMARY KEY NOT NULL, nombre VARCHAR NOT NULL)"
query_create_cursos = "CREATE TABLE coreografias(id SERIAL PRIMARY KEY NOT NULL, titulo VARCHAR NOT NULL, descripcion VARCHAR NOT NULL, portada VARCHAR NOT NULL, estado BOOLEAN, coreografo_id INTEGER REFERENCES coreografos, ritmo_id INTEGER REFERENCES ritmos, user_id INTEGER REFERENCES users)"
query_create_reseñas = "CREATE TABLE comentarios(id SERIAL PRIMARY KEY NOT NULL, comentario VARCHAR, user_id INTEGER REFERENCES users, coreo_id INTEGER REFERENCES coreografias)"
query_create_videos = "CREATE TABLE videos(id SERIAL PRIMARY KEY NOT NULL, enlace VARCHAR NOT NULL, coreo_id INTEGER REFERENCES coreografias)"
query_create_likes = "CREATE TABLE likes(id SERIAL PRIMARY KEY NOT NULL, me_gusta BOOLEAN, coreo_id INTEGER NOT NULL REFERENCES coreografias, user_id INTEGER NOT NULL REFERENCES users)"


### Crea las tablas usando las querys
db.execute(query_create_users)
db.execute(query_create_coreagrafos)
db.execute(query_create_ritmos)
db.execute(query_create_cursos)
db.execute(query_create_reseñas)
db.execute(query_create_videos)
db.execute(query_create_likes)

db.commit()

ritmos = ("Ballet","Tango","Rock & Roll","Vals Francés o Pericón","Vals Inglés","Bachata","Bolero","Cha-cha-chá","Cumbia", "Kizomba", "Mambo", "Merengue", "Salsa y Rueda Cubana", "Samba", "Reggaetón", "Hip Hop", "K-pop", "Break dance")

for rit in ritmos:
    db.execute(f"insert into ritmos (nombre) values ('{rit}')")

db.commit()

db.commit()

coreografos = ("Aurélien Bory", "Pierre Rigal", "Maurice Béjart", "Benjamin Millepied", "Carolyn Carlson", "Marie-Claude Pietragalla", "Kamel Ouali", "Mia Frye", "Wade Robson", "Blanca Li")
nacionalidad = ("Francia", "Francia", "Bélgica", "Estados Unidos", "Estados Unidos", "Francia", "Francia", "Estados Unidos", "Estados Unidos", "España")

for i in range(10):
    db.execute(f"INSERT INTO coreografos (nombre, nacionalidad) VALUES ('{coreografos[i]}', '{nacionalidad[i]}')")
db.commit()

#db.execute("ALTER TABLE users ADD perfil VARCHAR") """

#db.execute("UPDATE likes set me_gusta = false where id = 1")
db.execute("TRUNCATE TABLE likes RESTART IDENTITY")
db.commit()

print("Tablas creadas")