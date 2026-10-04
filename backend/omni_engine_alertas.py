import requests
import math
import time

# ==========================================
# 1. BASE DE ATIVOS CORPORATIVOS (Nossa Infraestrutura)
# ==========================================
ATIVOS_EMPRESA = [
    {"nome": "Plataforma Petrobras P-77 (Pre-Sal)", "lat": -23.8, "lon": -42.2, "tipo": "PETROLEO"},
    {"nome": "Mina de Ferro Carajas (Vale)", "lat": -6.0, "lon": -50.1, "tipo": "MINERACAO"},
    {"nome": "Fazenda de Soja (Mato Grosso)", "lat": -12.5, "lon": -55.7, "tipo": "AGRONEGOCIO"},
    # Coloquei este navio estrategicamente na rota do Furacao Marie que vimos no seu log!
    {"nome": "Navio Sonda (Rota Pacifico)", "lat": 21.5, "lon": -120.0, "tipo": "PETROLEO"}
]

# ==========================================
# 2. CALCULO MATEMATICO ESPACIAL (Haversine)
# ==========================================
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """Calcula a distancia real em KM entre dois pontos no globo terrestre."""
    R = 6371  # Raio da Terra em KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ==========================================
# 3. OMNI-ENGINE (Cruzamento NASA x Petrobras)
# ==========================================
def rodar_motor_georreferencial():
    print("[OMNI-ENGINE] Iniciando rastreio global de ativos...")
    print("[NASA] Baixando coordenadas orbitais ao vivo...\n")
    
    url = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&category=wildfires,severeStorms"
    
    try:
        resposta = requests.get(url)
        eventos = resposta.json().get('events', [])
        
        # Para cada infraestrutura nossa, varremos os desastres da NASA
        for ativo in ATIVOS_EMPRESA:
            print(f"Monitorando: {ativo['nome']}...")
            perigo_detectado = False
            
            for evento in eventos:
                # Pegando a ultima coordenada do desastre
                geometria = evento['geometry'][-1] 
                lon_nasa, lat_nasa = geometria.get('coordinates')
                
                # Calcula a distancia entre o desastre e a nossa plataforma
                distancia = calcular_distancia_km(ativo['lat'], ativo['lon'], lat_nasa, lon_nasa)
                
                # Regra de Negocio: Se o desastre estiver a menos de 500 KM, dispara alerta!
                if distancia < 500:
                    perigo_detectado = True
                    print(f"  --> [ALERTA VERMELHO CRITICO] Risco Iminente detectado!")
                    print(f"  --> AMEACA: {evento.get('title')}")
                    print(f"  --> DISTANCIA: Apenas {distancia:.2f} KM de colisao/impacto.")
                    print(f"  --> ACAO IA: Bloqueando operacao e iniciando protocolo de evacuacao!\n")
                    break # Para a busca deste ativo pois ja achou perigo
            
            if not perigo_detectado:
                print("  --> [STATUS SEGURO] Nenhum desastre natural no raio de 500km.\n")
                
    except Exception as e:
        print(f"[ERRO] Falha no cruzamento de dados: {e}")

if __name__ == "__main__":
    rodar_motor_georreferencial()
