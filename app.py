from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import uuid

app = Flask(__name__)

# Configuração do banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'purchase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de compra
class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    localizador = db.Column(db.String(36), unique=True, nullable=False)
    voo_id = db.Column(db.Integer, nullable=False)
    passageiros = db.Column(db.Text, nullable=False)  # JSON como string
    e_tickets = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Purchase Service rodando com banco de dados!", 200

@app.route('/comprar', methods=['POST'])
def comprar():
    data = request.get_json()
    voo_id = data.get('voo_id')
    passageiros = data.get('passageiros')

    if not voo_id or not passageiros:
        return jsonify({"erro": "Dados incompletos"}), 400

    localizador = str(uuid.uuid4())
    e_tickets = [str(uuid.uuid4()) for _ in passageiros]

    nova_compra = Compra(
        localizador=localizador,
        voo_id=voo_id,
        passageiros=str(passageiros),
        e_tickets=str(e_tickets)
    )
    db.session.add(nova_compra)
    db.session.commit()

    return jsonify({
        "mensagem": "Compra realizada com sucesso",
        "localizador": localizador,
        "e_tickets": e_tickets
    }), 201

@app.route('/compras', methods=['GET'])
def listar_compras():
    compras = Compra.query.all()
    return jsonify([{
        "id": c.id,
        "localizador": c.localizador,
        "voo_id": c.voo_id,
        "passageiros": c.passageiros,
        "e_tickets": c.e_tickets
    } for c in compras]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)