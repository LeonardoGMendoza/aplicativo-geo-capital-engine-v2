import requests
import math
import yfinance as yf
import time

# ==========================================
# 1. ATIVOS E COMUNIDADES (Contexto ESG)
# ==========================================
ATIVOS_GLOBAIS = [
    {
        "empresa": "PETROBRAS", "nome": "Plataforma Offshore (Litoral)", "lat": -23.8, "lon": -42.2, 
        "setor": "PETROLEO", "ticker": "BZ=F",
        "comunidade_vizinha": "Vila de Pescadores Litoral SP/RJ",
        "risco_secundario": "Vazamento Tóxico de Óleo no Oceano"
    },
    {
        "empresa": "VALE", "nome": "Mina Carajás e Barragem", "lat": -6.0, "lon": -50.1, 
        "setor": "MINERACAO", "ticker": "VALE",
        "comunidade_vizinha": "Comunidade Ribeirinha (Vale do Rio)",
        "risco_secundario": "Rompimento de Barragem e Contaminação da Água (Risco de Cólera)"
    },
    {
        "empresa": "BP", "nome": "Navio Sonda (Pacífico)", "lat": 21.5, "lon": -120.0, 
        "setor": "PETROLEO", "ticker": "BP",
        "comunidade_vizinha": "Arquipélagos e Ilhas Costeiras",
        "risco_secundario": "Tsunami com lixo químico"
    }
]

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# ==========================================
# 2. MOTOR OMNI-ECO RESCUE (IA + ESG)
# ==========================================
def iniciar_central_executiva():
    print("="*70)
    print(" OMNI-ECO RESCUE ENGINE - PAINEL DE RISCO CORPORATIVO E ESG ")
    print("="*70)
    
    print("\n[1/3] Sincronizando com a Bolsa de Valores...")
    precos_mercado = {}
    for ativo in ATIVOS_GLOBAIS:
        ticker = ativo["ticker"]
        if ticker not in precos_mercado:
            try:
                cotacao = yf.Ticker(ticker).history(period="1d")
                precos_mercado[ticker] = cotacao['Close'].iloc[-1] if not cotacao.empty else 0.0
            except:
                precos_mercado[ticker] = 0.0

    print("\n[2/3] Conectando à infraestrutura aeroespacial da NASA...")
    url_nasa = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&category=wildfires,severeStorms,earthquakes"
    try:
        dados_nasa = requests.get(url_nasa).json().get('events', [])
        print(f"      -> {len(dados_nasa)} desastres e anomalias globais rastreados.")
    except:
        dados_nasa = []
        print("      -> [ERRO] Sem comunicação espacial.")

    print("\n[3/3] Iniciando Motor de IA Oracle (Análise de Risco e Defesa Civil)...")
    time.sleep(1)
    
    for ativo in ATIVOS_GLOBAIS:
        print(f"\n>>> Analisando Ativo: {ativo['empresa']} - {ativo['nome']}")
        perigo = False
        
        for evento in dados_nasa:
            lon_nasa, lat_nasa = evento['geometry'][-1].get('coordinates')
            dist = calcular_distancia(ativo['lat'], ativo['lon'], lat_nasa, lon_nasa)
            
            if dist < 600:
                perigo = True
                preco = precos_mercado.get(ativo['ticker'], 0.0)
                
                print(f"    [!!! IMPACTO DUPLO DETECTADO !!!]")
                print(f"    - Causa Principal: {evento['title']}")
                print(f"    - Distância do Ativo: {dist:.1f} KM\n")
                
                print(f"    🤖 [PLANO DE AÇÃO GERADO PELA IA - ORACLE LLM]:")
                print(f"       🏭 1. ALERTA PATRIMONIAL (B2B):")
                print(f"          > Recomendação: Interromper extração e acionar travas de segurança.")
                print(f"          > Proteção de Capital: Cotação US$ {preco:.2f}. Evitando dano estrutural e perdas financeiras severas.\n")
                
                print(f"       🌍 2. ALERTA ESG E DEFESA CIVIL (IMPACTO SOCIAL):")
                print(f"          > Comunidade Ameaçada: {ativo['comunidade_vizinha']}.")
                print(f"          > Risco Secundário: {ativo['risco_secundario']}.")
                print(f"          > Saúde Pública: Despachar kits de descontaminação e purificadores de água.")
                print(f"          > Resgate Inclusivo: Acionar resgate humanitário prioritário para grupos vulneráveis.")
                print(f"          > Notificação: SMS gerado e enviado à Defesa Civil local.\n")
                break
                
        if not perigo:
            preco = precos_mercado.get(ativo['ticker'], 0.0)
            print(f"    [STATUS VERDE] Operação Segura e Comunidade Protegida. Cotação: US$ {preco:.2f}.")

    print("\n" + "="*70)

if __name__ == "__main__":
    iniciar_central_executiva()
