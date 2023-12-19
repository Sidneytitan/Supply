function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    var draggedElement = document.getElementById(data);
    var destinationBlock = ev.currentTarget;

    // Verifica se o destino é "Pedidos Finalizados"
    if (destinationBlock.id === "done") {
        // Adiciona um botão de exclusão ao cartão
        var deleteButton = document.createElement("button");
        deleteButton.innerHTML = "Excluir";
        deleteButton.onclick = function () {
            // Adicionar lógica para excluir do MongoDB se necessário
            var itemId = draggedElement.id;
            excluirPedido(itemId, function () {
                // Remove o cartão ao clicar no botão de exclusão
                draggedElement.remove();
                // Atualizar a contagem de cartões em "Pedidos Finalizados" após excluir o cartão
                updateDoneCount();
            });
        };
        draggedElement.appendChild(deleteButton);
    }

    // Verifica se o destino é "Pedidos Pendentes"
    if (destinationBlock.id === "todo") {
        // Adiciona o cartão acima do botão de cadastro
        destinationBlock.insertBefore(draggedElement, destinationBlock.lastElementChild);
    } else {
        // Adiciona o cartão normalmente
        destinationBlock.appendChild(draggedElement);
    }

    // Salvar a posição atual no armazenamento local
    salvarPosicaoCartoes();

    // Atualizar a contagem de cartões em "Pedidos Pendentes"
    updateTodoCount();
    // Atualizar a contagem de cartões em "Realizando Orçamentos"
    updateInProgressCount();

    // Atualizar a contagem de cartões em "Pedidos Finalizados"
    if (destinationBlock.id === "done") {
        updateDoneCount();
    }
}

function createTask() {
    var x = document.getElementById("inprogress");
    var y = document.getElementById("done");
    var z = document.getElementById("create-new-task-block");
    if (x.style.display === "none") {
        x.style.display = "block";
        y.style.display = "block";
        z.style.display = "none";
    } else {
        x.style.display = "none";
        y.style.display = "none";
        z.style.display = "flex";
    }
}

function saveTask() {
    var title = document.getElementById("new-task-title").value;
    var description = document.getElementById("new-task-description").value;
    var status = document.getElementById("new-task-status").value;

    // Enviar dados ao servidor usando fetch ou outra técnica
    fetch('/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'new-task-title': title,
            'new-task-description': description,
            'new-task-status': status,
        }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Exibir mensagem de sucesso ou erro

        // Adicionar lógica para atualizar a lista de pedidos no DOM
        if (data.success) {
            // Atualizar a posição dos cartões sem recarregar a página
            salvarPosicaoCartoes();

            // Criar o HTML do novo cartão
            var newCardHTML = createCardHTML(data.taskId, title, description, status);

            // Adicionar o novo cartão à coluna apropriada
            var destinationColumn = document.getElementById(status.toLowerCase());
            destinationColumn.insertAdjacentHTML('beforeend', newCardHTML);

            // Atualizar contagem de pedidos
            updateTodoCount();
            updateInProgressCount();
            updateDoneCount();
        }
    })
    .catch(error => {
        console.error('Erro ao enviar dados:', error);
    });
}



function editTask() {
    var saveButton = document.getElementById("save-button");
    var editButton = document.getElementById("edit-button");
    if (saveButton.style.display === "none") {
        saveButton.style.display = "block";
        editButton.style.display = "none";
    } else {
        saveButton.style.display = "none";
        editButton.style.display = "block";
    }
}

function excluirPedido(itemId, callback) {
    // Enviar solicitação ao servidor para excluir o pedido do MongoDB
    fetch('/delete/' + itemId, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Exibir mensagem de sucesso ou erro
        // Adicionar lógica para atualizar a página ou a lista de cards se necessário

        // Chamar o callback após excluir o pedido
        if (typeof callback === 'function') {
            callback();
        }
    })
    .catch(error => {
        console.error('Erro ao excluir pedido:', error);
    });
}

function salvarPosicaoCartoes() {
    var todo = document.getElementById("todo");
    var inProgress = document.getElementById("inprogress");
    var done = document.getElementById("done");

    var posicaoCartoes = {
        "todo": obterIdsCartoes(todo),
        "inprogress": obterIdsCartoes(inProgress),
        "done": obterIdsCartoes(done)
    };

    // Salvar no armazenamento local
    localStorage.setItem("posicaoCartoes", JSON.stringify(posicaoCartoes));
}

function obterIdsCartoes(container) {
    var cartoes = container.getElementsByClassName("task");
    var ids = Array.from(cartoes).map(cartao => cartao.id);
    return ids;
}

function updateTodoCount() {
    var todoBlock = document.getElementById("todo");
    var todoCountElement = document.getElementById("todo-count");
    var todoCount = todoBlock.getElementsByClassName("task").length;
    todoCountElement.innerHTML = ` (${todoCount} Pedidos)`;   //escrita do contador
}

function updateInProgressCount() {
    var inProgressBlock = document.getElementById("inprogress");
    var inProgressCountElement = document.getElementById("inprogress-count");
    var inProgressCount = inProgressBlock.getElementsByClassName("task").length;
    inProgressCountElement.innerHTML = ` (${inProgressCount} Pedidos)`;
}

function updateDoneCount() {
    var doneBlock = document.getElementById("done");
    var doneCountElement = document.getElementById("done-count");
    var doneCount = doneBlock.getElementsByClassName("task").length;
    doneCountElement.innerHTML = ` (${doneCount} Pedidos)`;
}

window.onload = function () {
    carregarPosicaoSalva();
    updateTodoCount();
    updateInProgressCount();
    updateDoneCount();
};

function carregarPosicaoSalva() {
    var posicaoSalva = localStorage.getItem("posicaoCartoes");

    if (posicaoSalva) {
        posicaoSalva = JSON.parse(posicaoSalva);

        // Mover cartões para as colunas correspondentes
        moverCartoesParaColuna("todo", posicaoSalva.todo);
        moverCartoesParaColuna("inprogress", posicaoSalva.inprogress);
        moverCartoesParaColuna("done", posicaoSalva.done);
    }
}

function moverCartoesParaColuna(colunaId, cartoesIds) {
    var coluna = document.getElementById(colunaId);

    if (!coluna || !cartoesIds) {
        return;
    }

    var fragmento = document.createDocumentFragment();

    for (var i = 0; i < cartoesIds.length; i++) {
        var cartao = document.getElementById(cartoesIds[i]);
        if (cartao) {
            fragmento.appendChild(cartao);
        }
    }

    coluna.appendChild(fragmento);
}

// Função para criar o HTML do novo cartão
function createCardHTML(taskId, title, description, status) {
    var deleteButtonHTML = '<button onclick="excluirPedido(' + taskId + ')">Excluir</button>';
    var cardHTML = '<div id="' + taskId + '" class="task" draggable="true" ondragstart="drag(event)">' +
        '<span><strong>Título:</strong> ' + title + '</span>' +
        '<span><strong>Descrição:</strong> ' + description + '</span>' +
        '<span><strong>Status:</strong> ' + status + '</span>' +
        (status.toLowerCase() === 'done' ? deleteButtonHTML : '') +
        '</div>';
    return cardHTML;
}
