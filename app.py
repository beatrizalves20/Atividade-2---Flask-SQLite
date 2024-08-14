import sqlite3
from flask import Flask, request, jsonify, g, abort
from Globals import DATABASE_NAME


app = Flask(__name__)

# Aqui era armazenar os dados especificos 
def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g ._database = sqlite3.connect(DATABASE_NAME)    
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:  #Verifica se a conexão com o banco de dados existe.
        db.close()
    
#    conn = None
#    try:
#       conn = sqlite3.connect(DATABASE_NAME)
#   except sqlite3.Error as e:
#        print('Não foi possível conectar')

#    return conn


@app.route("/")
def index():
    return (jsonify({"versao": 1}), 200)


def getUsuarios():
    conn = get_db_connection()
    cursor  = conn.cursor()
    resultset = cursor.execute('SELECT * FROM tb_usuario').fetchall()
    usuarios = []
    for linha in resultset:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
        usuarios.append(usuarioDict)
    conn.close()
    return usuarios


def setUsuario(data):
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')
    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f'INSERT INTO tb_usuario(nome, nascimento) values ("{nome}", "{nascimento}")')
    conn.commit()
    id = cursor.lastrowid
    data['id'] = id
    conn.close()
    # Retornar o usuário criado.
    return data


@app.route("/usuarios", methods=['GET', 'POST'])
def usuarios():
    if request.method == 'GET':
        # Listagem dos usuários
        usuarios = getUsuarios()
        return jsonify(usuarios), 200
    elif request.method == 'POST':
        # Recuperar dados da requisição: json.
        data = request.json
        data = setUsuario(data)
        return jsonify(data), 201


def getUsuarioById(id):
    usuarioDict = None
    conn = get_db_connection()
    cursor = conn.cursor()
    linha = cursor.execute(
        f'SELECT * FROM tb_usuario WHERE id = {id}').fetchone()
    if linha is not None:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
    conn.close()
    return usuarioDict


def updateUsuario(id, data):
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')

    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tb_usuario SET nome = ?, nascimento = ? WHERE id = ?', (nome, nascimento, id))
    conn.commit()

    rowupdate = cursor.rowcount

    conn.close()
    # Retornar a quantidade de linhas.
    return rowupdate

#Rota para deletar um id (DELETE)
@app.route("/deleteUsuario<int:id>", methods=['DELETE'] )
def deleteUsuario(id):
    usuario = next((usuario for usuario in  usuario if usuario['id'] == id)), None

    if usuario:
        usuarios.remover(id)
        return jsonify({'message': 'id do usuario excluído'})
    
    else:
        return jsonify({'message': 'id do usuario não encontrado'}), 404


#    conn = get_db_connection()
#    cursor = conn.cursor()
    
#    try:                         
        # VERIFICAR SE O USUÁRIO EXISTE 
#        cursor.execute('SELECT * FROM usuario WHERE id= ?', (id))
#        usuario = cursor.fetchone()

#        if usuario is None:
#           abort(404, description="Usuário não encontrado")

        #DELETE O USUÁRIO    
#        cursor.execute('DELETE FROM usuarios WHERE id = ?',(id))
#        conn.commit()

#       return jsonify({'message': 'Usuário deletado com sucesso'}), 200

#     except sqlite3.DatabaseError as e:
#         conn.rollback() #Reverter qualquer alteração em caso de erro 
#         return jsonify({'error': 'Erro ao acessar o banco de dados', 'message': str(e)}), 500

#    finally: 
#        conn.close() #Garantir que a conexão seja fechada



@app.route("/usuarios/<int:id>", methods=['GET', 'DELETE', 'PUT'])
def usuario(id):
    if request.method == 'GET':
        usuario = getUsuarioById(id)
        if usuario is not None:
            return jsonify(usuario), 200
        else:
            return {}, 404
    elif request.method == 'PUT':
        # Recuperar dados da requisição: json.
        data = request.json
        rowupdate = updateUsuario(id, data)
        if rowupdate != 0:
            return (data, 201)
        else:
            return (data, 304)
