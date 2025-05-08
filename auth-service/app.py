from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)

# Configuração do banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'auth.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

# Inicializa o banco (só na primeira vez)
with app.app_context():
    db.create_all()

# Lista simulada de sessões (em memória)
sessoes = {}

@app.route('/')
def index():
    return "Auth Service rodando com banco de dados!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(email=email, senha=senha).first()
    if usuario:
        chave = str(uuid.uuid4())
        sessoes[chave] = email
        return jsonify({"mensagem": "Login efetuado", "chave": chave}), 200
    return jsonify({"erro": "Credenciais inválidas"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    chave = request.get_json().get('chave')
    if chave in sessoes:
        sessoes.pop(chave)
        return jsonify({"mensagem": "Logout efetuado"}), 200
    return jsonify({"erro": "Sessão inválida"}), 400

@app.route('/validate-session', methods=['GET'])
def validate_session():
    chave = request.args.get('chave')
    if chave in sessoes:
        return jsonify({"valido": True, "usuario": sessoes[chave]}), 200
    return jsonify({"valido": False}), 401

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"erro": "Usuário já cadastrado"}), 409

    novo_usuario = Usuario(email=email, senha=senha)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuário registrado com sucesso"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    
# “Esse Dockerfile cria um ambiente minimalista em Python 3.10, copia os arquivos da API, instala as dependências, e configura o container para rodar
# o serviço Flask quando for iniciado. Com isso, temos um microserviço independente, leve e pronto para ser orquestrado via Kubernetes.”