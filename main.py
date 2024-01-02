from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# Configuração do MongoDB
app.config['MONGO_URI'] = "mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/supply"
mongo = PyMongo(app)

# Conectar a diferentes coleções
collection_pedido = mongo.db.pedido
collection_cotacao = mongo.db.cotacao
collection_lista_fornecedor = mongo.db.lista_fornecedor
collection_gestao_pedido = mongo.db.gestao_pedido




# Rota para exibir a página inicial
@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/pedido')
def pedido():
    # Busca todos os pedidos no banco de dados
    dados_kanban = list(collection_pedido.find())
    return render_template('pedido.html', dados_kanban=dados_kanban)

# Rota para adicionar um novo pedido
@app.route('/add', methods=['POST'])
def add():
    # Obtém dados do formulário
    titulo = request.form.get('new-task-title')
    descricao = request.form.get('new-task-description')
    status = request.form.get('new-task-status')

    # Insere o novo pedido no banco de dados
    new_task = {'titulo': titulo, 'descricao': descricao, 'status': status}
    result = collection_pedido.insert_one(new_task)

    # Retorna a resposta em formato JSON
    return jsonify({'success': True, 'message': 'Pedido adicionado com sucesso!', 'taskId': str(result.inserted_id)})

# Rota para excluir um pedido
@app.route('/delete/<pedido_id>', methods=['DELETE'])
def delete(pedido_id):
    # Remove o pedido do banco de dados pelo ID
    collection_pedido.delete_one({'_id': ObjectId(pedido_id)})

    return jsonify({'message': 'Pedido excluído com sucesso', 'success': True})

# Rota para a página Kanban
@app.route('/kanban')
def kanban():
    # Obtendo dados do MongoDB
    dados_kanban = list(collection_cotacao.find())
    return render_template('kanban.html', dados_kanban=dados_kanban)

# Rota para obter todas as cotações
@app.route('/dados_kanban', methods=['GET'])
def get_dados_kanban():
    # Obtendo dados do MongoDB
    dados_kanban = list(collection_cotacao.find())

    # Converter ObjectId para str para torná-lo serializável em JSON
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

        # Recupere o ID da cotação recém-criada
        novo_item_id = str(novo_item.inserted_id)

        return jsonify({'success': True, 'message': 'Cotação criada com sucesso!', 'taskId': novo_item_id})

    return jsonify({'success': False, 'message': 'Falha ao criar cotação.'})

# Rota para mover um item para uma nova coluna
@app.route('/mover_item_coluna/<item_id>/<nova_coluna>', methods=['PUT'])
def mover_item_coluna(item_id, nova_coluna):
    # Atualizar o status do item no MongoDB
    collection_cotacao.update_one(
        {'_id': ObjectId(item_id)},
        {'$set': {'status': nova_coluna}}
    )
    return jsonify({'message': 'Item movido com sucesso!'})

# Rota para excluir uma cotação
@app.route('/excluir_cotacao/<item_id>', methods=['DELETE'])
def excluir_cotacao(item_id):
    try:
        # Excluir o item do MongoDB
        result = collection_cotacao.delete_one({'_id': ObjectId(item_id)})

        if result.deleted_count == 1:
            return jsonify({'message': 'Cotação excluída com sucesso!'})
        else:
            return jsonify({'error': 'Cotação não encontrada'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para exibir a lista de fornecedores
@app.route('/listafornecedor')
def lista_fornecedor():
    # Obtendo dados do MongoDB
    data_list = list(collection_lista_fornecedor.find())
    return render_template('index.html', data_list=data_list)



# Rota para exibir o formulário de adição
@app.route('/adicionar', methods=['GET'])
def exibir_formulario_adicao():
    return render_template('adicionar.html')

# Rota para lidar com a adição de fornecedores (POST)
@app.route('/adicionar_fornecedor', methods=['POST'])
def adicionar_fornecedor():
    if request.method == 'POST':
        novo_fornecedor = {
            'fornecedor': request.form['fornecedor'],
            'cnpj': request.form['cnpj'],
            'telefone': request.form['telefone'],
            'responsavel': request.form['responsavel'],
            'local': request.form['local'],
            'cep': request.form['cep'],
            'Ramo': request.form['ramo'],
            'Forma_pagamento': request.form['forma_pagamento']
        }

        # Insere o fornecedor no MongoDB
        collection_lista_fornecedor.insert_one(novo_fornecedor)

    return redirect(url_for('lista_fornecedor'))

# Rota para exibir o formulário de exclusão
@app.route('/excluir', methods=['GET', 'POST'])
def exibir_formulario_exclusao():
    if request.method == 'POST':
        # Obtendo o nome do fornecedor a ser excluído do formulário
        excluir = request.form['Fornecedor']

        # Excluir o fornecedor pelo nome
        collection_lista_fornecedor.delete_one({'fornecedor': excluir})

        return redirect(url_for('lista_fornecedor'))

    return render_template('excluir.html')

# Adicione uma rota para lidar com a pesquisa
@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    # Obter os parâmetros da pesquisa
    filtro = request.args.get('filtro')
    termo = request.args.get('termo')

    # Construir a consulta MongoDB com base nos parâmetros de pesquisa
    query = {filtro: {'$regex': termo, '$options': 'i'}}
    data_list = list(collection_lista_fornecedor.find(query))

    return render_template('index.html', data_list=data_list)

# Rota para exibir a lista de pedidos novo codigo
# Rota para exibir a lista de pedidos
@app.route('/listapedido')
def lista_pedido():
    # Obtendo dados do MongoDB na coleção gestao_pedido
    data_list = list(collection_gestao_pedido.find())
    return render_template('gestao_pedido.html', data_list=data_list)


# Rota para exibir o formulário de adição de pedidos
@app.route('/adicionar_pedido', methods=['GET'])
def exibir_formulario_adicao_pedido():
    return render_template('adicionar_pedido.html')

# Rota para lidar com a adição de pedidos (POST)
@app.route('/adicionar_pedido', methods=['POST'])
def adicionar_pedido():
    if request.method == 'POST':
        novo_pedido = {
            'numero_pedido': request.form['numero_pedido'],
            'filial': request.form['filial'],
            'fornecedor': request.form['fornecedor'],
            'status': request.form['status'],
            'observacao': request.form['observacao']
        }

        # Insere o pedido no MongoDB
        collection_gestao_pedido.insert_one(novo_pedido)


    return redirect(url_for('lista_pedido'))


# Rota para exibir o formulário de exclusão de pedidos
@app.route('/excluir_pedido', methods=['GET', 'POST'])
def exibir_formulario_exclusao_pedido():
    if request.method == 'POST':
        # Obtendo o número do pedido a ser excluído do formulário
        numero_pedido = request.form.get('numero_pedido')

        # Excluir o pedido pelo número do pedido
        collection_gestao_pedido.delete_one({'numero_pedido': numero_pedido})


        return redirect(url_for('lista_pedido'))

    return render_template('excluir_pedido.html')


# Adicione uma rota para lidar com a pesquisa de pedidos
@app.route('/pesquisar_pedido', methods=['GET'])
def pesquisar_pedido():
    # Obter os parâmetros da pesquisa
    filtro = request.args.get('filtro')
    termo = request.args.get('termo')

    # Construir a consulta MongoDB com base nos parâmetros de pesquisa
    query = {filtro: {'$regex': termo, '$options': 'i'}}
    data_list = list(collection_gestao_pedido.find(query))

    return render_template('gestao_pedido.html', data_list=data_list)


@app.route('/atualizar_filial', methods=['POST'])
def atualizar_filial():
    # Lógica para atualizar a filial no banco de dados
    # Certifique-se de que você está recebendo os dados corretamente do frontend
    data = request.get_json()
    nova_filial = data['novaFilial']
    pedido_id = data['pedidoId']

    # Sua lógica de atualização aqui

    # Exemplo de resposta (você pode personalizar conforme necessário)
    return jsonify({'status': 'success', 'message': 'Filial atualizada com sucesso'})


@app.route('/atualizar_status', methods=['POST'])
def atualizar_status():
    # Lógica para atualizar o status no banco de dados
    # Certifique-se de que você está recebendo os dados corretamente do frontend
    data = request.get_json()
    novo_status = data['novoStatus']
    pedido_id = data['pedidoId']

    # Sua lógica de atualização aqui

    # Exemplo de resposta (você pode personalizar conforme necessário)
    return jsonify({'status': 'success', 'message': 'Status atualizado com sucesso'})


if __name__ == "__main__":
    app.run(debug=True)

#Anotação

#  <!-- Footer Section -->
    #<footer>Sidney Ribeiro</footer>