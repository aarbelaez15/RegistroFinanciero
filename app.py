from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from io import BytesIO
from reportlab.pdfgen import canvas
from sqlalchemy import desc


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/ingresos'
db = SQLAlchemy(app)

@app.route('/generar_pdf', methods=['GET', 'POST'])
def generar_pdf():
    if request.method == 'POST':
        fecha_str = request.form.get('fecha')
        fecha = datetime.strptime(fecha_str, '%Y-%m')
        total = db.session.query(func.sum(RegistroFinanciero.monto)).scalar() or 0.0

        with app.app_context():
            registros = RegistroFinanciero.query.filter(db.func.extract('year', RegistroFinanciero.fecha) == fecha.year,
                                                        db.func.extract('month', RegistroFinanciero.fecha) == fecha.month).all()

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.drawString(100, 800, f"Registros Financieros - {fecha.strftime('%B %Y')}")
        pdf.drawString(100, 770, f"Estado actual:  {total}")
        pdf.drawString(100, 740, " Monto")
        pdf.drawString(200, 740, " Fecha")
        pdf.drawString(320, 740, " Descripción")
        pdf.drawString(500, 740, " Tipo")


        y_position = 730
        for registro in registros:
            y_position -= 20

            pdf.drawString(100, y_position, f" ${registro.monto}")
            pdf.drawString(200, y_position, f" {registro.fecha.strftime('%Y-%m-%d')}")
            pdf.drawString(320, y_position, f" {registro.descripcion}")
            pdf.drawString(500, y_position, f" {registro.tipo}")

        pdf.save()

        buffer.seek(0)
        response = make_response(buffer.read())
        response.mimetype = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=registros_{fecha.year}_{fecha.month}.pdf'

        return response
    return redirect(url_for('index'))

class RegistroFinanciero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

@app.route('/')
def index():
    with app.app_context():
        total = db.session.query(func.sum(RegistroFinanciero.monto)).scalar() or 0.0
        registros = RegistroFinanciero.query.order_by(desc(RegistroFinanciero.fecha)).limit(5).all()

    return render_template('index.html', registros=registros, total=total)


@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    with app.app_context():
        total = db.session.query(func.sum(RegistroFinanciero.monto)).scalar() or 0.0

        if request.method == 'POST':
            monto = float(request.form['monto'])
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
            descripcion = request.form['descripcion']
            tipo = request.form['tipo']

            nuevo_registro = RegistroFinanciero(monto=monto, fecha=fecha, descripcion=descripcion, tipo=tipo)
            db.session.add(nuevo_registro)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template('agregar.html', total=total)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)