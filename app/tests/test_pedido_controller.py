import pytest
from fastapi.testclient import TestClient
from unittest import mock
from main import app  # Supondo que o arquivo principal da aplicação seja `main.py`
from app.controllers import router
from app.models.schemas import Pedido

# Criando o cliente de testes do FastAPI
client = TestClient(app)

# Mockando a resposta da requisição de produtos
def mock_get_produtos_com_estoque(*args, **kwargs):
    return mock.Mock(status_code=200, json=lambda: [{"produto": "Produto 1", "quantidade": 10}])

# Testando o endpoint /produtos-disponiveis
@mock.patch("requests.get", side_effect=mock_get_produtos_com_estoque)
def test_obter_produtos_com_estoque(mock_get):
    response = client.get("/produtos-disponiveis")
    assert response.status_code == 200
    assert response.json() == [{"produto": "Produto 1", "quantidade": 10}]
    mock_get.assert_called_once_with("http://busca-produto:8080/produtos-disponiveis")

# Mockando o banco de dados para o endpoint /pedido
@pytest.fixture
def mock_session():
    with mock.patch("app.controllers.sqs.SessionLocal") as mock_session:
        mock_session.return_value.execute.return_value.inserted_primary_key = [1]
        yield mock_session

# Testando o endpoint /pedido
def test_criar_pedido(mock_session):
    pedido_data = {
        "cliente_id": 1,
        "status": "Em andamento",
        "produtos": [
            {"produto": "Produto 1", "preco": 100.0, "quantidade": 2}
        ]
    }
    response = client.post("/pedido", json=pedido_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Pedido criado com sucesso", "id": 1}

# Mockando a resposta da consulta do banco de dados
def mock_query_pedido(*args, **kwargs):
    return mock.Mock(fetchone=lambda: mock.Mock(
        id=1, preco_total=200.0, status="Em andamento", cliente_id=1, cliente_nome="João", cliente_email="joao@email.com", cliente_cpf="12345678901"))

def mock_query_produtos(*args, **kwargs):
    return mock.Mock(fetchall=lambda: [mock.Mock(produto="Produto 1", preco=100.0, quantidade=2)])

# Testando o endpoint /pedido/{pedido_id}
@mock.patch("app.controllers.sqs.SessionLocal")
@mock.patch("app.controllers.sqs.SessionLocal().execute", side_effect=[mock_query_pedido(), mock_query_produtos()])
def test_visualizar_pedido(mock_execute, mock_session):
    response = client.get("/pedido/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "preco_total": 200.0,
        "status": "Em andamento",
        "cliente": {
            "id": 1,
            "nome": "João",
            "email": "joao@email.com",
            "cpf": "12345678901"
        },
        "produtos": [
            {"produto": "Produto 1", "preco": 100.0, "quantidade": 2}
        ]
    }

# Testando quando o pedido não é encontrado
def test_visualizar_pedido_nao_encontrado():
    with mock.patch("app.controllers.sqs.SessionLocal().execute", side_effect=[mock.Mock(fetchone=lambda: None)]):
        response = client.get("/pedido/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Pedido não encontrado"}
