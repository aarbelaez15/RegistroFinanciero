# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'efectivo' o 'bancario'
