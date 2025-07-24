# 🏢 QUALICENTRAL - Sistema de Gestão da Qualidade

*Centralizando e automatizando processos de qualidade para o recebimento de insumos na indústria.*

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

### 🚀 **Aplicação em Nuvem**

**[Acesse a aplicação aqui!](https://sistemaqualidade.streamlit.app/)**

---

### 📸 **Captura de Tela**

[Captura de Tela da Aplicação](TELA INICIAL DO SITE.png)

---

## 📝 Sobre o Projeto

O **QUALICENTRAL** é um projeto para desenvolver um sistema web focado em otimizar e digitalizar o controle de qualidade no recebimento de insumos para indústrias alimentícias. O objetivo é substituir planilhas e controles manuais por um fluxo de trabalho centralizado, rastreável e eficiente, desde o cadastro do fornecedor até a emissão de laudos de não conformidade.

---

## ✨ Funcionalidades

### Funcionalidades Implementadas

* **Módulo 1: Cadastro de Fornecedores**
    * Formulário completo para cadastro de novos fornecedores.
    * Armazenamento de dados persistente em um banco de dados **SQLite**.
    * Validação para impedir o cadastro de **CNPJs duplicados**.
    * Visualização em tabela de todos os fornecedores já cadastrados na base de dados.
    * Interface limpa e organizada em uma aplicação **Streamlit** com múltiplas páginas.

### 🗺️ Roadmap de Funcionalidades Planejadas

-   [ ] **Módulo 2: Agendamento de Entregas:** Permitir que fornecedores agendem entregas, com dados do veículo e da carga.
-   [ ] **Módulo 3: Painel Interno de Visualização:** Um dashboard para a equipe interna visualizar e gerenciar o status dos veículos agendados.
-   [ ] **Módulo 4: Análise de Recebimento:** Lançamento de resultados de análises de qualidade para cada lote recebido.
-   [ ] **Módulo 5: Registro de Não Conformidades:** Sistema para registrar desvios de qualidade, gerar laudos e comunicar fornecedores.
-   [ ] **Automação:** Envio automático de laudos e notificações por e-mail e/ou WhatsApp.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Framework Web:** Streamlit
* **Banco de Dados:** SQLite
* **Manipulação de Dados:** Pandas

---

## ⚙️ Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

**Pré-requisitos:**
* Python 3.8 ou superior
* `pip` (gerenciador de pacotes do Python)

**Passos:**

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Laianne27/Sistema_Qualidade.git](https://github.com/Laianne27/Sistema_Qualidade.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd Sistema_Qualidade
    ```

3.  **Crie e ative um ambiente virtual (recomendado):**
    * *Um ambiente virtual isola as dependências do seu projeto, evitando conflitos com outras bibliotecas instaladas no seu sistema.*
    ```bash
    # Cria o ambiente
    python -m venv .venv

    # Ativa o ambiente (Linux/macOS)
    source .venv/bin/activate

    # Ativa o ambiente (Windows)
    .\.venv\Scripts\activate
    ```

4.  **Instale as dependências:**
    * *O arquivo `requirements.txt` lista todas as bibliotecas que o projeto precisa.*
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run 0_🏠_Início.py
    ```

O seu navegador abrirá automaticamente com a aplicação em funcionamento!

---

## 📂 Estrutura do Projeto

```
Sistema_Qualidade/
│
├── 0_🏠_Início.py             # Script da página principal (boas-vindas)
├── pages/                    # Pasta para as subpáginas da aplicação
│   ├── 1_Cadastro de Fornecedores.py
│   └── ...
├── fornecedores.db           # Arquivo do banco de dados SQLite
├── requirements.txt          # Lista de dependências Python do projeto
└── README.md                 # Este arquivo de descrição
```