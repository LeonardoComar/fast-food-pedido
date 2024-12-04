import pytest
from fastapi.testclient import TestClient
from unittest import mock
from main import app  # Supondo que o arquivo principal da aplicação seja `main.py`
from app.models.schemas import Cliente

# Criando o cliente de testes do FastAPI
client = TestClient(app)

# Mockando o banco de dados para o endpoint /cliente
@pytest.fixture
def mock_session():
    with mock.patch("app.controllers.cliente.SessionLocal") as mock_session:
        mock_session.return_value.execute.return_value.lastrowid = 1  # Simula o id do cliente inserido
        yield mock_session

# Testando o endpoint /cliente para criar um cliente
def test_criar_cliente(mock_session):
    # Dados do cliente
    cliente_data = {
        "nome": "João da Silva",
        "email": "joao@email.com",
        "cpf": "12345678901"
    }

    # Realizando a requisição POST para o endpoint /cliente
    response = client.post("/cliente", json=cliente_data)
    
    # Verificando se a resposta está correta
    assert response.status_code == 200
    assert response.json() == {"message": "Cliente criado com sucesso", "id": 1}

# Testando quando ocorre um erro ao tentar criar o cliente
def test_criar_cliente_erro(mock_session):
    with mock.patch("app.controllers.cliente.SessionLocal().execute", side_effect=Exception("Erro de banco de dados")):
        cliente_data = {
            "nome": "Maria Souza",
            "email": "maria@email.com",
            "cpf": "98765432100"
        }

        # Realizando a requisição POST para o endpoint /cliente
        response = client.post("/cliente", json=cliente_data)

        # Verificando se a resposta é um erro
        assert response.status_code == 400
        assert response.json() == {"detail": "Erro de banco de dados"}
