# 📦 Inventário Checkout

Sistema Fullstack com integração de hardware (RFID) para gestão de ativos físicos e ferramentas.

## DEMO 📸:

https://github.com/user-attachments/assets/4dcf6af3-1cb7-4307-825d-dd4e1a78b90f

## 🚀 Tecnologias
- **Back-end:** Python com Flask.
- **Front-end:** HTML, CSS e JavaScript.
- **Banco de Dados:** SQLite.
- **Hardware:** Módulo Leitor RFID e microcontrolador (Arduino via comunicação Serial).

## 🛠️ Funcionalidades
- Integração em tempo real entre leitura de hardware (RFID) e interface web.
- Controle de ferramentas e equipamentos com preenchimento inteligente via sensor.
- Controle de acessos e permissões (RBAC - Administradores e Alunos).
- Registro de logs e histórico de movimentação (Retiradas, Devoluções e responsáveis).
- Interface reativa assíncrona, eliminando a necessidade de recarregamento da página.

## 📁 Estrutura do Projeto
- `/static` e `/templates`: Interface do usuário padronizada e dividida em componentes (UI).
- `/routes` e `/database`: Lógica modularizada do servidor, regras de negócio e persistência (API).
- Scripts C++ do microcontrolador para varredura e transmissão serial.

---
Desenvolvido por Icaro de Souza de Lima
