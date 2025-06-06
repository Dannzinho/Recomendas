# RECOMENDAS

Sistema de recomendação de produtos que combina filtragem baseada em conteúdo e colaborativa, com interface gráfica e banco de dados relacional.

--- 

## 🎯 Objetivo

O sistema Recomendas tem como objetivo oferecer recomendações personalizadas de produtos para cada usuário, utilizando algoritmos de filtragem baseada em conteúdo e filtragem colaborativa, ele resolve o problema da sobrecarga de opções em catálogos grandes, ajudando os usuários a encontrarem rapidamente produtos relevantes ao seu perfil e preferências,
a motivação do projeto surge da ampla aplicação prática dos sistemas de recomendação em plataformas modernas como e-commerces, serviços de streaming e redes sociais, além disso, o projeto serve como um exercício completo de integração entre algoritmos de inteligência artificial, persistência de dados com banco relacional, interface gráfica e estruturação de dados, a estrutura de lista encadeada foi incluída como uma aplicação prática do conteúdo de estruturas de dados, sendo usada para gerenciar o histórico de visualizações recentes de produtos por usuário. Isso permite armazenar, atualizar e percorrer esse histórico de forma eficiente, reforçando o vínculo entre teoria e prática no desenvolvimento do sistema.

---

## 👨‍💻 Tecnologias Utilizadas

Liste as principais tecnologias, linguagens, frameworks e bibliotecas utilizadas:

- Python 3.12
- PostgreSQL
- SQLAlchemy

## 🗂️ Estrutura do Projeto


A estrutura a seguir é um exemplo. Vocês devem usar a estrutura do seu projeto obrigatóriamente. 
```
📦 RECOMENDAS
├── 📁 src
│   ├── 📁 algorithms
│   │   ├── __init__.py
│   │   ├── collaborative.py
│   │   └── content_based.py
│   │
│   ├── 📁 data
│   │   ├── __init__.py
│   │   ├── categories.json
│   │   ├── initial_data_loader.py
│   │   ├── products.json
│   │   └── users.json
│   │
│   ├── 📁 database
│   │   ├── __init__.py
│   │   └── db_manager.py
│   │
│   ├── 📁 structures
│   │   ├── __init__.py
│   │   └── linked_list.py
│   │
│   ├── 📁 ui
│   │   ├── __init__.py
│   │   ├── gui_interface.py
│   │   └── logo.png
│   │
│   ├── 📁 utils
│   │   ├── __init__.py
│   │   └── recommendation_manager.py
│   │
│   └── main.py
│
├── 📁 tests
│   ├── test_algorithms.py
│   └── test_linked_list.py
│
└── readme.md
|
└── requirements.txt


---

## ⚙️ Como Executar

### ✅ Rodando Localmente

1. Clone o repositório:

```
git clone https://github.com/Dannzinho/Recomendas/tree/main
cd Recomendas
```

2. Crie o ambiente virtual e ative:

```
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

3. Instale as dependências:

```
pip install -r requirements.txt
```

4. exporte o banco de dados após cria-lo no postgre:

```
python -m src.data.initial_data_loader
```

6. Execute a aplicação:


```
python -m src.main
```

---


## 👥 Equipe

| Nome | GitHub |
|------|--------|
| Daniel Vieira Santos | [@dannzinhow](https://github.com/Dannzinho) |
| Kevin dos Santos Vieira
| Eduardo Alvez dos Reis

---

## 🧠 Disciplinas Envolvidas

- Estrutura de Dados I

---

## 🏫 Informações Acadêmicas

- Universidade: **Universidade Braz Cubas**
- Curso: **Ciência da Computação / Análise e Desenvolvimento de Sistemas**
- Semestre: 2º
- Período: Noite
- Professora orientadora: **Dra. Andréa Ono Sakai**
- Evento: **Mostra de Tecnologia 1º Semestre de 2025**
- Local: Laboratório 12
- Data: 06 de junho de 2025

---

## 📄 Licença

MIT License — sinta-se à vontade para utilizar, estudar e adaptar este projeto.
