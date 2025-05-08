from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flight.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de voo
class Voo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origem = db.Column(db.String(10), nullable=False)
    destino = db.Column(db.String(10), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    lugares_disponiveis = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Flight Service rodando com banco de dados!", 200

@app.route('/voos', methods=['GET'])
def listar_voos():
    voos = Voo.query.all()
    return jsonify([{
        "id": v.id,
        "origem": v.origem,
        "destino": v.destino,
        "data": v.data,
        "preco": v.preco,
        "lugares_disponiveis": v.lugares_disponiveis
    } for v in voos]), 200

@app.route('/voos/pesquisar', methods=['GET'])
def pesquisar_voos():
    origem = request.args.get('origem')
    destino = request.args.get('destino')
    data_voo = request.args.get('data')

    query = Voo.query
    if origem:
        query = query.filter_by(origem=origem)
    if destino:
        query = query.filter_by(destino=destino)
    if data_voo:
        query = query.filter_by(data=data_voo)

    voos = query.all()
    return jsonify([{
        "id": v.id,
        "origem": v.origem,
        "destino": v.destino,
        "data": v.data,
        "preco": v.preco,
        "lugares_disponiveis": v.lugares_disponiveis
    } for v in voos]), 200

@app.route('/voos/pesquisar-menor-tarifa', methods=['GET'])
def pesquisar_menor_tarifa():
    origem = request.args.get('origem')
    destino = request.args.get('destino')
    data_voo = request.args.get('data')
    passageiros = int(request.args.get('passageiros', 1))

    voos = Voo.query.filter_by(origem=origem, destino=destino, data=data_voo).filter(
        Voo.lugares_disponiveis >= passageiros).order_by(Voo.preco).all()

    return jsonify([{
        "id": v.id,
        "origem": v.origem,
        "destino": v.destino,
        "data": v.data,
        "preco": v.preco,
        "lugares_disponiveis": v.lugares_disponiveis
    } for v in voos]), 200

@app.route('/voos/adicionar', methods=['POST'])
def adicionar_voo():
    data = request.get_json()
    voo = Voo(
        origem=data['origem'],
        destino=data['destino'],
        data=data['data'],
        preco=data['preco'],
        lugares_disponiveis=data['lugares_disponiveis']
    )
    db.session.add(voo)
    db.session.commit()
    return jsonify({"mensagem": "Voo adicionado com sucesso"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)