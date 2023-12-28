document.addEventListener("DOMContentLoaded", function() {
    var adicionarBtn = document.getElementById("adicionarBtn");

    adicionarBtn.addEventListener("click", function(event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        var fornecedor = document.querySelector("input[name='fornecedor']").value;
        var cnpj = document.querySelector("input[name='cnpj']").value;

        // Continue pegando os outros valores conforme necessário

        if (!fornecedor || !cnpj) {
            alert("Por favor, preencha os campos Fornecedor e CNPJ.");
        } else {
            // Se os campos estão preenchidos, envie o formulário
            document.getElementById("registroForm").submit();
        }
    });
});

// Coloque aqui o conteúdo do seu JavaScript para abrir/fechar o modal
function openCadastroModal() {
    document.getElementById('cadastroModal').style.display = 'block';
}

function closeCadastroModal() {
    document.getElementById('cadastroModal').style.display = 'none';
}
