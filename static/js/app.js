let ultimaTagLida = null;

async function checarLeitura() {
    try {
        const res = await fetch('/api/scan');
        const dados = await res.json();

        document.getElementById('leitor-nome').innerText = dados.nome;
        document.getElementById('leitor-tag').innerText = dados.tag_id ? `RFID: ${dados.tag_id}` : `RFID: -- --`;
        document.getElementById('leitor-detalhes').innerText = dados.detalhes;

        const img = document.getElementById('leitor-foto');
        const placeholder = document.getElementById('placeholder');

        if (dados.foto) {
            img.src = dados.foto; img.style.display = 'block'; placeholder.style.display = 'none';
        } else {
            img.style.display = 'none'; placeholder.style.display = 'block';
        }

        if (dados.conhecido) {
            document.getElementById('p-status').style.display = 'block';
            document.getElementById('p-local').style.display = 'block';

            const elStatus = document.getElementById('leitor-status');
            elStatus.innerText = dados.status;
            elStatus.className = dados.status === 'Ativo' ? 'badge-status status-ativo' : 'badge-status status-inativo';
            document.getElementById('leitor-local').innerText = dados.localizacao;

            // Lógica dos Botões de Movimentação
            const btnAcao = document.getElementById('btn-movimentar');
            btnAcao.style.display = 'block';
            if (dados.status === 'Ativo') {
                btnAcao.innerText = "Registrar Retirada 📤";
                btnAcao.style.background = "#e63946";
            } else {
                btnAcao.innerText = "Registrar Devolução 📥";
                btnAcao.style.background = "#52b788";
            }
        } else {
            document.getElementById('p-status').style.display = 'none';
            document.getElementById('p-local').style.display = 'none';
            document.getElementById('btn-movimentar').style.display = 'none';
        }

        // Verifica se o formulário existe na tela (se é admin) e preenche a Tag nova
        const inputTagForm = document.getElementById('form-tag');
        if (inputTagForm && dados.tag_id && !dados.conhecido && dados.tag_id !== ultimaTagLida) {
            inputTagForm.value = dados.tag_id;
            ultimaTagLida = dados.tag_id;
        }

    } catch (e) {
        // Ignora erros silenciosos se o backend estiver reiniciando
    }
}

async function registrarMovimentacao() {
    // Pega a Tag lida no exato momento do clique
    let tag = document.getElementById('leitor-tag').innerText.replace('RFID:', '').trim();
    
    if (!tag || tag === '-- --') {
        mostrarToast("Nenhuma tag válida na leitora.", "erro");
        return;
    }

    try {
        const res = await fetch('/api/movimentar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag_id: tag })
        });
        
        const dados = await res.json();
        
        if (res.ok) {
            mostrarToast(`${dados.acao} registrada com sucesso!`, "sucesso");
            
            // Atualiza a grid e o histórico na mesma hora!
            if(typeof carregarEstoque === 'function') carregarEstoque();
            if(typeof carregarHistorico === 'function') carregarHistorico();
            
        } else {
            mostrarToast(dados.erro || "Erro ao registrar.", "erro");
        }
    } catch(e) { 
        console.error(e); 
        mostrarToast("Erro de conexão.", "erro");
    }
}

async function carregarHistorico() {
    try {
        const res = await fetch('/api/movimentacoes');
        const dados = await res.json();
        const tbody = document.getElementById('corpo-tabela-historico');

        if (dados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="data-vazia">Nenhuma movimentação ainda.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        dados.forEach(mov => {
            const dev_style = mov.data_devolucao === 'Em uso' ? 'color: #ff8585; font-weight:bold;' : '';

            tbody.innerHTML += `
                        <tr>
                            <td style="color:#7B3FE4;">${mov.tag_id}</td>
                            <td><strong>${mov.equipamento}</strong></td>
                            <td>${mov.usuario}</td>
                            <td>${mov.data_retirada}</td>
                            <td style="${dev_style}">${mov.data_devolucao}</td>
                        </tr>
                    `;
        });
    } catch (e) { console.error(e); }
}

async function carregarEstoque() {
    try {
        const res = await fetch('/api/produtos');
        const produtos = await res.json();
        const grid = document.getElementById('grid-produtos');
        grid.innerHTML = '';
        produtos.forEach(prod => {
            const statusClass = prod.status === 'Ativo' ? 'status-ativo' : 'status-inativo';
            grid.innerHTML += `
                        <div class="card-produto">
                            <span class="mini-status ${statusClass}">${prod.status}</span>
                            <img src="${prod.foto || 'https://via.placeholder.com/220x120?text=Sem+Foto'}" alt="Foto">
                            <div style="font-size: 0.7rem; color: #7B3FE4; font-weight:bold;">${prod.tag_id}</div>
                            <strong style="font-size: 0.95rem; display:block;">${prod.nome}</strong>
                        </div>`;
        });
    } catch (e) { }
}


async function salvarProduto() {
    const tagId = document.getElementById('form-tag').value;
    const nome = document.getElementById('form-nome').value;
    const status = document.getElementById('form-status').value;
    const localizacao = document.getElementById('form-localizacao').value;
    const detalhes = document.getElementById('form-detalhes').value;
    const fotoInput = document.getElementById('form-foto');

    if (!tagId || !nome) {
        mostrarToast("A Tag RFID e o Nome são obrigatórios!", "erro");
        return;
    }

    const formData = new FormData();
    formData.append('tag_id', tagId);
    formData.append('nome', nome);
    formData.append('status', status);
    formData.append('localizacao', localizacao);
    formData.append('detalhes', detalhes);
    
    if (fotoInput.files.length > 0) {
        formData.append('foto', fotoInput.files[0]);
    }

    try {
        const res = await fetch('/api/cadastrar', { method: 'POST', body: formData });
        const dados = await res.json();

        if (res.ok) {
            mostrarToast("Equipamento cadastrado com sucesso!", "sucesso");
            
            // Limpa o formulário
            document.getElementById('form-tag').value = '';
            document.getElementById('form-nome').value = '';
            document.getElementById('form-localizacao').value = '';
            document.getElementById('form-detalhes').value = '';
            fotoInput.value = '';
            
            // Chama as funções para recarregar a tela na hora!
            if(typeof carregarEstoque === 'function') carregarEstoque();
            
        } else {
            mostrarToast(dados.erro || "Erro ao salvar.", "erro");
        }
    } catch (e) {
        console.error(e);
        mostrarToast("Falha na comunicação com o servidor.", "erro");
    }
}

function mudarAba(aba) {
    // Esconde tudo primeiro
    document.getElementById('aba-scanner').classList.remove('ativa');
    document.getElementById('aba-historico').classList.remove('ativa');
    document.getElementById('tela-scanner').style.display = 'none';
    document.getElementById('tela-historico').style.display = 'none';
    
    // Controle dinâmico para a aba de usuários (se ela existir na tela)
    const abaUser = document.getElementById('aba-usuarios');
    const telaUser = document.getElementById('tela-usuarios');
    if (abaUser) {
        abaUser.classList.remove('ativa');
        telaUser.style.display = 'none';
    }

    // Ativa a aba clicada
    document.getElementById('aba-' + aba).classList.add('ativa');
    document.getElementById('tela-' + aba).style.display = aba === 'scanner' ? 'flex' : 'block';

    // Dispara a busca no banco dependendo da aba
    if (aba === 'historico') carregarHistorico();
    if (aba === 'usuarios') carregarUsuarios();
}


// Função global para gerar alertas bonitos
function mostrarToast(mensagem, tipo = 'sucesso') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.innerText = mensagem;
    container.appendChild(toast);

    // Mata o toast depois de 3 segundos
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-in reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- INICIALIZAÇÃO DO SISTEMA ---
// Inicia o loop que fica escutando o leitor RFID a cada 1 segundo
setInterval(checarLeitura, 1000);

// Carrega a grade de produtos assim que a página abre
carregarEstoque();

// Função para destruir a sessão e voltar pro Login
async function fazerLogout() {
    try {
        const res = await fetch('/api/logout', { method: 'POST' });
        if (res.ok) {
            window.location.href = '/login';
        }
    } catch (e) {
        console.error("Erro ao deslogar:", e);
    }
}

// --- Acoes usuarios DB ---

async function carregarUsuarios() {
    try {
        const res = await fetch('/api/usuarios');
        const dados = await res.json();
        const tbody = document.getElementById('corpo-tabela-usuarios');
        tbody.innerHTML = '';
        
        dados.forEach(user => {
            const badgeClass = user.cargo === 'admin' ? 'status-ativo' : 'status-inativo';
            tbody.innerHTML += `
                <tr>
                    <td>#${user.id}</td>
                    <td><strong>${user.nome}</strong></td>
                    <td><span class="mini-status ${badgeClass}">${user.cargo.toUpperCase()}</span></td>
                    <td>
                        <button onclick="deletarUsuario(${user.id})" style="background: #e63946; padding: 5px 10px; font-size: 0.8rem; margin:0;">Excluir</button>
                    </td>
                </tr>
            `;
        });
    } catch (e) { console.error(e); }
}

async function salvarUsuario() {
    const nome = document.getElementById('user-nome').value;
    const senha = document.getElementById('user-senha').value;
    const cargo = document.getElementById('user-cargo').value;

    if (!nome || !senha) return mostrarToast("Preencha nome e senha!", "erro");

    try {
        const res = await fetch('/api/usuarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, senha, cargo })
        });
        const dados = await res.json();

        if (res.ok) {
            mostrarToast("Usuário criado com sucesso!", "sucesso");
            document.getElementById('user-nome').value = '';
            document.getElementById('user-senha').value = '';
            carregarUsuarios(); // Recarrega a tabela na hora
        } else {
            mostrarToast(dados.erro, "erro");
        }
    } catch (e) { mostrarToast("Erro na conexão", "erro"); }
}

async function deletarUsuario(id) {
    if (!confirm("Tem certeza que deseja excluir este acesso?")) return;

    try {
        const res = await fetch(`/api/usuarios/${id}`, { method: 'DELETE' });
        const dados = await res.json();
        if (res.ok) {
            mostrarToast("Usuário removido!", "sucesso");
            carregarUsuarios();
        } else {
            mostrarToast(dados.erro, "erro");
        }
    } catch (e) { mostrarToast("Erro ao deletar", "erro"); }
}
