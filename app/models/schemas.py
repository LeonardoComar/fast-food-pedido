from pydantic import BaseModel, field_validator
from typing import List

class Cliente(BaseModel):
    id: int = None
    nome: str = None
    email: str = None
    cpf: str = None
    anonimo: bool = False

    @field_validator("nome", "email", mode="before", check_fields=True)
    @classmethod
    def validar_campos_anonimos(cls, value, info):
        anonimo = info.data.get("anonimo", False)
        if not anonimo and not value:
            raise ValueError(f"O campo '{info.field_name}' é obrigatório para clientes não anônimos.")
        if anonimo and value:
            raise ValueError(f"O campo '{info.field_name}' deve estar vazio para clientes anônimos.")
        return value

class ProdutoItem(BaseModel):
    produto: str
    preco: float
    quantidade: int

class Pedido(BaseModel):
    id: int = None
    preco_total: float = None
    produtos: List[ProdutoItem]
    status: str = "Recebido"
    cliente_id: int

    @field_validator("preco_total", mode="before", check_fields=True)
    @classmethod
    def calcular_preco_total(cls, value, values):
        if "produtos" in values:
            total = sum(p.preco * p.quantidade for p in values["produtos"])
            if total <= 0:
                raise ValueError("Preço total deve ser maior que zero")
            return total
        return value
