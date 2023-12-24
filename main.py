from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/supply"
app.config['SECRET_KEY'] = 'secretpassword'
mongo = PyMongo(app)
socketio = SocketIO(app)

collection_pedido = mongo.db.pedido
collection_cotacao = mongo.db.cotacao
collection_lista_fornecedor = mongo.db.lista_fornecedor


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/pedido')
def pedido():
    dados_kanban = list(collection_pedido.find())
    return render_template('pedido.html', dados_kanban=dados_kanban)


@app.route('/add', methods=['POST'])
def add():
    titulo = request.form.get('new-task-title')
    descricao = request.form.get('new-task-description')
    status = request.form.get('new-task-status')

    new_task = {'titulo': titulo, 'descricao': descricao, 'status': status}
    result = collection_pedido.insert_one(new_task)

    emit_kanban_update()

    return jsonify({'success': True, 'message': 'Pedido adicionado com sucesso!', 'taskId': str(result.inserted_id)})


@app.route('/delete/<pedido_id>', methods=['DELETE'])
def delete(pedido_id):
    collection_pedido.delete_one({'_id': ObjectId(pedido_id)})

    emit_kanban_update()

    return jsonify({'message': 'Pedido excluído com sucesso', 'success': True})


@app.route('/kanban')
def kanban():
    dados_kanban = list(collection_cotacao.find())
    return render_template('kanban.html', dados_kanban=dados_kanban)


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

        emit_kanban_update()

        return jsonify({'success': True, 'message': 'Cotação criada com sucesso!', 'taskId': novo_item_id})

    return jsonify({'success': False, 'message': 'Falha ao criar cotação.'})


# Rota para mover um item para uma nova coluna
@app.route('/mover_item_coluna/<item_id>/<nova_coluna>', methods=['PUT'])
def mover_item_coluna(item_id, nova_coluna):
    try:
        # Atualizar o status do item no MongoDB
        collection_pedido.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {'status': nova_coluna}}
        )
        return jsonify({'message': 'Item movido com sucesso!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/excluir_cotacao/<item_id>', methods=['DELETE'])
def excluir_cotacao(item_id):
    try:
        result = collection_cotacao.delete_one({'_id': ObjectId(item_id)})

        if result.deleted_count == 1:
            emit_kanban_update()
            return jsonify({'message': 'Cotação excluída com sucesso!'})
        else:
            return jsonify({'error': 'Cotação não encontrada'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    emit_kanban_update()


def emit_kanban_update():
    socketio.emit('update_kanban', broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True)

#Anotação

#  <!-- Footer Section -->
    #<footer>Sidney Ribeiro</footer>