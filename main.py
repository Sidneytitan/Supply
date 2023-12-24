from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_socketio import SocketIO, disconnect

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/supply"
mongo = PyMongo(app)
socketio = SocketIO(app)

# Conectar a diferentes coleções
collection_pedido = mongo.db.pedido
collection_cotacao = mongo.db.cotacao
collection_lista_fornecedor = mongo.db.lista_fornecedor

# Restante do código...

# Rota para exibir a página inicial
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Rota para exibir a página de pedidos
@app.route('/pedido')
def pedido():
    dados_kanban = list(collection_pedido.find())
    return render_template('pedido.html', dados_kanban=dados_kanban)

# Restante do código...

# Rota para obter todas as cotações
@app.route('/dados_kanban', methods=['GET'])
def get_dados_kanban():
    dados_kanban = list(collection_cotacao.find())
    dados_kanban_serializable = [
        {
            "_id": str(dado["_id"]),
            "titulo": dado["titulo"],
            "descricao": dado["descricao"],
            "status": dado["status"]
        }
        for dado in dados_kanban
    ]
    return jsonify({'dados_kanban': dados_kanban_serializable})

# Rota para adicionar um novo item ao Kanban
@app.route('/criar_cotacao', methods=['POST'])
def criar_cotacao():
    data = request.form
    if 'new-task-title' in data and 'new-task-description' in data:
        novo_item = collection_cotacao.insert_one({
            'titulo': data['new-task-title'],
            'descricao': data['new-task-description'],
            'status': data['new-task-status']
        })

        novo_item_id = str(novo_item.inserted_id)
        socketio.emit('atualizar_kanban', namespace='/kanban', broadcast=True)
        return jsonify({'success': True, 'message': 'Cotação criada com sucesso!', 'taskId': novo_item_id})

    return jsonify({'success': False, 'message': 'Falha ao criar cotação.'})

# Rota para mover um item para uma nova coluna
@app.route('/mover_item_coluna/<item_id>/<nova_coluna>', methods=['PUT'])
def mover_item_coluna(item_id, nova_coluna):
    collection_cotacao.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {'status': nova_coluna}}
    )
    socketio.emit('atualizar_kanban', namespace='/kanban', broadcast=True)
    return jsonify({'message': 'Item movido com sucesso!'})

# Restante do código...

# Função para lidar com a conexão de um cliente via WebSocket
@socketio.on('connect', namespace='/kanban')
def handle_connect():
    print('Client connected')

# Função para lidar com a desconexão de um cliente via WebSocket
@socketio.on('disconnect', namespace='/kanban')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True)

#Anotação

#  <!-- Footer Section -->
    #<footer>Sidney Ribeiro</footer>