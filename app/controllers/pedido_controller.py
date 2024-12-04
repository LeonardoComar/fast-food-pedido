from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.models.database import SessionLocal
from app.models.tables import pedido, produto_pedido, cliente
from app.models.schemas import Pedido
import json
import requests
from app.controllers.sqs import send_to_sqs

router = APIRouter()

SQS_UPDATE_QUEUE = "pedido-atualizacao"

# Endpoints para pedido
@router.get("/produtos-disponiveis")
def obter_produtos_com_estoque():
    url = "http://busca-produto:8080/produtos-disponiveis"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for error HTTP status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar produtos: {e}")
        return None

@router.post("/pedido")
async def criar_pedido(pedido_data: Pedido):
    session = SessionLocal()
    try:
        # Calcula o preço total se ele ainda não estiver definido
        preco_total = sum(
            produto.preco * produto.quantidade for produto in pedido_data.produtos
        )
        
        # Insere o pedido na tabela `pedido`
        insert_pedido_query = pedido.insert().values(
            preco_total=preco_total,
            status=pedido_data.status,
            cliente_id=pedido_data.cliente_id
        )
        result = session.execute(insert_pedido_query)
        pedido_id = result.inserted_primary_key[0]  # ID do pedido recém-criado

        # Insere os produtos na tabela `produto_pedido`
        produtos = []
        for produto in pedido_data.produtos:
            insert_produto_pedido_query = produto_pedido.insert().values(
                pedido_id=pedido_id,
                produto=produto.produto,
                preco=produto.preco,
                quantidade=produto.quantidade
            )
            session.execute(insert_produto_pedido_query)

            # Adiciona o produto ao array de produtos para a mensagem
            produtos.append({
                "produto": produto.produto,
                "quantidade": produto.quantidade,
                # "descricao": produto.descricao if produto.descricao else ""
                "descricao": ""
            })

        session.commit()

        # Construindo a mensagem para enviar à fila
        mensagem = {
            "pedido_id": pedido_id,
            "produtos": produtos
        }

        # Enviando a mensagem para a fila
        send_to_sqs(SQS_UPDATE_QUEUE, json.dumps(mensagem))
        
        return {"message": "Pedido criado com sucesso", "id": pedido_id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


@router.get("/pedido/{pedido_id}")
async def visualizar_pedido(pedido_id: int):
    session = SessionLocal()
    try:
        # Consulta para obter as informações do pedido
        query_pedido = select(
            pedido.c.id,
            pedido.c.preco_total,
            pedido.c.status,
            pedido.c.cliente_id,
            cliente.c.nome.label("cliente_nome"),
            cliente.c.email.label("cliente_email"),
            cliente.c.cpf.label("cliente_cpf")
        ).select_from(
            pedido.join(cliente, pedido.c.cliente_id == cliente.c.id)
        ).where(pedido.c.id == pedido_id)
        pedido_result = session.execute(query_pedido).fetchone()

        if not pedido_result:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        # Consulta para obter os produtos associados ao pedido
        query_produtos = select(
            produto_pedido.c.produto,
            produto_pedido.c.preco,
            produto_pedido.c.quantidade
        ).where(produto_pedido.c.pedido_id == pedido_id)
        produtos_result = session.execute(query_produtos).fetchall()

        # Construir a resposta
        pedido_data = {
            "id": pedido_result.id,
            "preco_total": pedido_result.preco_total,
            "status": pedido_result.status,
            "cliente": {
                "id": pedido_result.cliente_id,
                "nome": pedido_result.cliente_nome,
                "email": pedido_result.cliente_email,
                "cpf": pedido_result.cliente_cpf,
            },
            "produtos": [
                {
                    "produto": produto.produto,
                    "preco": produto.preco,
                    "quantidade": produto.quantidade
                }
                for produto in produtos_result
            ]
        }

        return pedido_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()
