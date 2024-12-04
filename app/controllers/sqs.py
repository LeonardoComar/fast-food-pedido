import boto3
import time
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from app.models.database import SessionLocal
from app.models.tables import pedido

# Inicializar cliente SQS
sqs = boto3.client('sqs',
                   endpoint_url='http://localstack:4566',
                   region_name='us-east-1',
                   aws_access_key_id='LKIAQAAAAAAAKWL2ASHI',
                   aws_secret_access_key='n327Qep6xt5SkDnWV8Lf7Ywb5U6C1B1rwtzoojba')

queues = {
    "producao-atualizacao": "http://localstack:4566/000000000000/producao-atualizacao"
}

def send_to_sqs(queue_name: str, message_body: str):
    try:
        # Get the URL for the queue
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        
        # Send the message
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )
    except Exception as e:
        print(f"Error sending message to SQS: {e}")

def handle_sqs_message(queue_name, queue_url):
    while True:
        try:
            messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
            
            if 'Messages' in messages:
                for message in messages['Messages']:                    
                    # Processa a mensagem
                    process_message(message, queue_name)
                    # Deleta a mensagem da fila em caso de sucesso
                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
            
            # Aguarda 5 segundos para a próxima obtenção de mensagens
            time.sleep(5)
        
        except Exception as e:
            print(f"Error processing message for queue {queue_name}: {str(e)}")
            time.sleep(10)

def process_message(message, queue_name):
    data = json.loads(message['Body'])  # Converte o corpo da mensagem de JSON para um dicionário
    session = SessionLocal()
    try:
        if queue_name == "producao-atualizacao":
            pedido_id = data.get("pedido_id")
            novo_status = data.get("novo_status")

            if not pedido_id or not novo_status:
                raise ValueError("JSON inválido: 'pedido_id' ou 'novo_status' ausente.")

            # Atualizar o status do pedido no banco de dados
            stmt = (
                update(pedido)
                .where(pedido.c.id == pedido_id)
                .values(status=novo_status)
            )
            session.execute(stmt)
            session.commit()
            print(f"Status do pedido {pedido_id} atualizado para '{novo_status}'.")

    except Exception as e:
        session.rollback()
        print(f"Erro ao processar mensagem: {e}")
        raise
    finally:
        session.close()
