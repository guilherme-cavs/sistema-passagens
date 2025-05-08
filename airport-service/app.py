from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'airport.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Aeroporto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)

class Destino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origem_id = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)
    destino_id = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Airport Service rodando com banco de dados!", 200

@app.route('/aeroportos', methods=['GET'])
def listar_aeroportos():
    aeroportos = Aeroporto.query.all()
    return jsonify([{
        "codigo": a.codigo,
        "nome": a.nome
    } for a in aeroportos]), 200

@app.route('/aeroportos-por-origem', methods=['GET'])
def destinos_por_origem():
    origem_codigo = request.args.get('origem')
    origem = Aeroporto.query.filter_by(codigo=origem_codigo).first()
    if not origem:
        return jsonify({"erro": "Aeroporto de origem não encontrado"}), 404

    destinos = Destino.query.filter_by(origem_id=origem.id).all()
    destinos_lista = []
    for d in destinos:
        destino = Aeroporto.query.get(d.destino_id)
        if destino:
            destinos_lista.append(destino.codigo)

    return jsonify({"origem": origem_codigo, "destinos": destinos_lista}), 200

@app.route('/aeroportos/adicionar', methods=['POST'])
def adicionar_aeroporto():
    data = request.get_json()
    codigo = data.get('codigo')
    nome = data.get('nome')
    if not codigo or not nome:
        return jsonify({"erro": "Dados incompletos"}), 400

    if Aeroporto.query.filter_by(codigo=codigo).first():
        return jsonify({"erro": "Aeroporto já cadastrado"}), 409

    novo = Aeroporto(codigo=codigo, nome=nome)
    db.session.add(novo)
    db.session.commit()
    return jsonify({"mensagem": "Aeroporto adicionado com sucesso"}), 201

@app.route('/destinos/adicionar', methods=['POST'])
def adicionar_destino():
    data = request.get_json()
    origem = Aeroporto.query.filter_by(codigo=data.get('origem')).first()
    destino = Aeroporto.query.filter_by(codigo=data.get('destino')).first()

    if not origem or not destino:
        return jsonify({"erro": "Código de origem ou destino inválido"}), 400

    novo = Destino(origem_id=origem.id, destino_id=destino.id)
    db.session.add(novo)
    db.session.commit()
    return jsonify({"mensagem": "Destino adicionado com sucesso"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)