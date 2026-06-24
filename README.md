# 📦 Inventário Checkout

Sistema Fullstack com integração de hardware (RFID) para gestão de ativos físicos e ferramentas.

## DEMO 📸:

https://github.com/user-attachments/assets/4dcf6af3-1cb7-4307-825d-dd4e1a78b90f

## 🚀 Tecnologias
- **Back-end:** Python com Flask.
- **Front-end:** HTML5, CSS3 e JavaScript (Vanilla, com consumo reativo de API).
- **Banco de Dados:** SQLite.
- **Hardware:** Módulo Leitor RFID e microcontrolador (Arduino via comunicação Serial).

## 🛠️ Funcionalidades
- Integração em tempo real entre leitura de hardware (RFID) e interface web.
- CRUD de ferramentas e equipamentos com preenchimento inteligente via sensor.
- Controle de acessos e permissões (RBAC - Administradores e Alunos).
- Registro de logs e histórico de movimentação (Retiradas, Devoluções e responsáveis).
- Interface reativa assíncrona, eliminando a necessidade de recarregamento da página.

## 📁 Estrutura do Projeto
- `/static` e `/templates`: Interface do usuário padronizada e dividida em componentes (UI).
- `/routes` e `/database`: Lógica modularizada do servidor, regras de negócio e persistência (API).
- Scripts C++ do microcontrolador para varredura e transmissão serial.

## ⚙️ Configuração e Execução (Rodando Localmente)

Siga os passos abaixo para testar o projeto na sua máquina:

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicialize o Banco de Dados e crie o Admin inicial:**
Como o sistema possui proteção de rotas, você precisa gerar o arquivo inventario_v2.db e criar o primeiro usuário administrador para conseguir logar. Execute o script de setup:

``` bash**
python criar_admin.py
```

**Usuário padrão genérico - Nome - Pessoa; Senha - 123**

3. **Inicie o Servidor:**

```bash
python app.py
```

Acesse o Sistema: Abra o navegador e acesse http://localhost:5000.

Desenvolvido por Icaro de Souza de Lima



