# C:\Users\Leonardo\Documents\Automacao\App-Geo-Capital-Engine\backend\pipeline_validador.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math

app = FastAPI(title="Omni-Capital Engine - Validador Híbrido", version="1.0")

# ==========================================
# 1. MODELOS DE DADOS
# ==========================================
class AlertaExterno(BaseModel):
    id_operacao: str
    lat: float
    lon: float
    tipo_alerta: str  # Ex: "VAZAMENTO_OLEO", "FOGO"
    confianca_api_externa: float # Confiança enviada pelo satélite/terceiro
    temperatura_local: float

# ==========================================
# 2. BANCO DE DADOS HISTÓRICO (Mock)
# Representa os dados armazenados no Oracle Autonomous DB
# ==========================================
HISTORICO_INTERNO = [
    {"lat": -23.5, "lon": -45.2, "tipo_alerta": "VAZAMENTO_OLEO", "falso_positivo": True, "temp": 35.0},
    {"lat": -23.6, "lon": -45.1, "tipo_alerta": "VAZAMENTO_OLEO", "falso_positivo": True, "temp": 34.5},
    {"lat": -20.1, "lon": -40.2, "tipo_alerta": "VAZAMENTO_OLEO", "falso_positivo": False, "temp": 22.0},
    {"lat": -20.0, "lon": -40.1, "tipo_alerta": "VAZAMENTO_OLEO", "falso_positivo": False, "temp": 21.5},
]

# ==========================================
# 3. LÓGICA DE FEW-SHOT RETRIEVAL
# ==========================================
def buscar_exemplos_similares(alerta: AlertaExterno, top_k: int = 2):
    """
    Busca no banco interno os eventos mais parecidos usando cálculo de distância simples.
    Na versão final, isso será feito por embeddings no Oracle Vector Store.
    """
    resultados = []
    for hist in HISTORICO_INTERNO:
        # Distância Euclidiana simples (Lat, Lon, Temp) para achar semelhança física
        distancia = math.sqrt(
            (alerta.lat - hist["lat"])**2 + 
            (alerta.lon - hist["lon"])**2 + 
            ((alerta.temperatura_local - hist["temp"]) * 0.1)**2 # Peso menor pra temp
        )
        resultados.append({"distancia": distancia, "dados": hist})
    
    # Ordena pelos mais próximos (menor distância) e pega os top_k (Few-Shot)
    resultados.sort(key=lambda x: x["distancia"])
    return [r["dados"] for r in resultados[:top_k]]

# ==========================================
# 4. ENDPOINT PRINCIPAL (O Escudo)
# ==========================================
@app.post("/api/v1/validar-alerta")
async def validar_alerta_satelite(alerta: AlertaExterno):
    """
    Recebe o alerta da API Externa (ex: Copernicus) e NÃO confia cegamente.
    Faz o Few-Shot Retrieval para validar a soberania da decisão.
    """
    # Passo 1: Busca o histórico interno (Few-Shot Retrieval)
    exemplos_parecidos = buscar_exemplos_similares(alerta, top_k=2)
    
    # Passo 2: Analisa se historicamente isso é falso positivo
    falsos_positivos = sum(1 for ex in exemplos_parecidos if ex["falso_positivo"])
    probabilidade_falso = falsos_positivos / len(exemplos_parecidos) if exemplos_parecidos else 0.0

    # Passo 3: Tomada de decisão Híbrida (Regra de Negócio)
    # Se a API externa diz que é perigo (confiança > 80%), mas nosso histórico
    # diz que naquelas condições 100% das vezes foi alarme falso:
    
    if alerta.confianca_api_externa >= 0.80 and probabilidade_falso == 1.0:
        decisao = "SUGESTÃO: BAIXO RISCO - possível falso positivo (requer validação humana)"
        motivo = f"Few-Shot Retrieval encontrou {falsos_positivos} casos similares no passado que eram Falsos Positivos. Evitando parada desnecessária da operação."
        risco_validado = "BAIXO"
        
    elif alerta.confianca_api_externa >= 0.80 and probabilidade_falso < 0.5:
        decisao = "ALERTA VALIDADO - REPASSAR PARA IA GENERATIVA (LLM)"
        motivo = "O histórico interno confirma o padrão de risco enviado pela API externa."
        risco_validado = "ALTO"
        
    else:
        decisao = "ANÁLISE HUMANA REQUERIDA"
        motivo = "Dados externos inconclusivos e sem histórico interno similar suficiente."
        risco_validado = "MÉDIO"

    return {
        "id_operacao": alerta.id_operacao,
        "input_externo": alerta.dict(),
        "few_shot_retrieval_usados": exemplos_parecidos,
        "status_soberania": decisao,
        "justificativa_motor": motivo,
        "risco_final": risco_validado
    }

# Instruções para rodar localmente no terminal:
# cd C:\Users\Leonardo\Documents\Automacao\App-Geo-Capital-Engine\backend
# pip install fastapi uvicorn pydantic
# uvicorn pipeline_validador:app --reload
