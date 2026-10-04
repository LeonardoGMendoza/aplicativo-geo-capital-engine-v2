# C:\Users\Leonardo\Documents\Automacao\App-Geo-Capital-Engine\dados_satelite\coletor_nasa.py

import requests
import json
import time

def coletar_eventos_nasa():
    """
    Fase 1 (Coleta Passiva): Conecta na API pública e oficial da NASA (EONET)
    para buscar anomalias ambientais (Desastres, Incêndios, Tempestades) 
    que estão acontecendo AGORA no planeta.
    """
    print("🛰️ [NASA EONET] Conectando aos satélites da NASA...")
    
    # URL da API de rastreamento de eventos da NASA (Aberta, sem necessidade de chave)
    url = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&category=wildfires,severeStorms"
    
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        dados = resposta.json()
        
        eventos = dados.get('events', [])
        print(f"✅ Sucesso! {len(eventos)} anomalias globais detectadas no momento.")
        
        # Filtra os 5 eventos mais recentes para não poluir a tela
        eventos_recentes = eventos[:5]
        
        print("\n--- ÚLTIMOS 5 ALERTAS DETECTADOS ---")
        for evento in eventos_recentes:
            titulo = evento.get('title')
            categoria = evento['categories'][0]['title']
            
            # Pega a última coordenada registrada pelo satélite
            geometria = evento['geometry'][-1] 
            coords = geometria.get('coordinates')
            data_alerta = geometria.get('date')
            
            print(f"🔥 ALERTA: {titulo}")
            print(f"   Categoria: {categoria}")
            print(f"   Data do Satélite: {data_alerta}")
            print(f"   Coordenadas (Lon, Lat): {coords}")
            print("-" * 40)
            
            # Aqui no futuro, nós pegaremos essas 'coords' e enviaremos
            # para o nosso 'pipeline_validador.py' validar!
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com a NASA: {e}")

if __name__ == "__main__":
    coletar_eventos_nasa()
    
# Instrução para rodar:
# cd C:\Users\Leonardo\Documents\Automacao\App-Geo-Capital-Engine\dados_satelite
# pip install requests
# python coletor_nasa.py
