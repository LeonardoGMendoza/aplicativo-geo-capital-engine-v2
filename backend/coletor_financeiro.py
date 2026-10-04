import yfinance as yf
import time

def coletar_dados_mercado():
    """
    Fase 2 (Coleta Financeira): Conecta na Bolsa de Valores 
    para buscar o preco ao vivo das Commodities.
    """
    print("[BOLSA DE VALORES] Conectando ao Yahoo Finance...")
    
    # Tickers das commodities na Bolsa:
    # BZ=F -> Petroleo Brent (Referencia global)
    # ZS=F -> Soja (Mercado Agricola)
    tickers = {
        "Petroleo Brent (Barril)": "BZ=F",
        "Soja (Saca)": "ZS=F"
    }
    
    print("\n--- COTACAO EM TEMPO REAL ---")
    for nome, simbolo in tickers.items():
        try:
            ativo = yf.Ticker(simbolo)
            # Pega o preco de fechamento do dia mais recente
            dados = ativo.history(period="1d")
            
            if not dados.empty:
                preco_atual = dados['Close'].iloc[-1]
                print(f"[COTAÇÃO] {nome}: US$ {preco_atual:.2f}")
            else:
                print(f"[AVISO] {nome}: Mercado fechado ou dados indisponiveis.")
                
        except Exception as e:
            print(f"[ERRO] Falha ao buscar {nome}: {e}")
            
    print("-" * 30)
    print("Essa e a informacao financeira que nossa IA usara para calcular prejuizos.")

if __name__ == "__main__":
    coletar_dados_mercado()
