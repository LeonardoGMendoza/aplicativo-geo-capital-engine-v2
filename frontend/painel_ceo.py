import os
import sys

# Adiciona a raiz do projeto ao Python para ele achar a pasta 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Adiciona o próprio diretório 'frontend' ao path para importar mapa_interativo
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from mapa_interativo import render_mapa_interativo

import math
import requests
import pandas as pd
import streamlit as st
import yfinance as yf
from backend.oracle_rag import gerar_recomendacao_rag

# ============================================================
# CONFIG GERAL DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Omni-EcoRescue",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DADOS: ATIVOS CORPORATIVOS (painel_ceo.py original)
# ============================================================
mapa_dados = [
    {"lat": 28.5,  "lon": -90.0,  "ativo": "Plataforma ExxonMobil (Golfo do Mexico)",  "comunidade_vizinha": "Vila de Pescadores de Nova Orleans",      "risco_secundario": "Vazamento Toxico (Oleoduto)"},
    {"lat": 29.0,  "lon": -88.0,  "ativo": "Plataforma Chevron (Golfo do Mexico)",      "comunidade_vizinha": "Comunidades Costeiras (Louisiana)",         "risco_secundario": "Contaminacao Hidrica (Oleoduto)"},
    {"lat": -23.8, "lon": -42.2,  "ativo": "Plataforma Petrobras (Pre-Sal, Brasil)",    "comunidade_vizinha": "Pescadores (Litoral de SP/RJ)",             "risco_secundario": "Vazamento no Mar e Destruicao de Manguezal"},
    {"lat": -6.0,  "lon": -50.1,  "ativo": "Mina Carajas Vale (Brasil)",                "comunidade_vizinha": "Comunidade Ribeirinha e Indigena",          "risco_secundario": "Rompimento de Barragem e Risco de Colera"},
    {"lat": -21.2, "lon": -47.8,  "ativo": "Usina Raízen (Sao Paulo)",                  "comunidade_vizinha": "Bairros Perifericos (Ribeirao Preto)",      "risco_secundario": "Fumaca Toxica e Incendios em Lavouras"},
    {"lat": 21.5,  "lon": -120.0, "ativo": "Navio Sonda BP (Pacifico)",                 "comunidade_vizinha": "Arquipelagos e Ilhas Costeiras",            "risco_secundario": "Tsunami com lixo quimico"},
]
df_ativos = pd.DataFrame(mapa_dados)

# ============================================================
# DADOS: ABRIGOS DE EVACUAÇÃO (omni_ecoresue_mvp.py original)
# ============================================================
ABRIGOS = [
    # Rio Grande do Sul (referência ao desastre das enchentes)
    {"nome": "Ginásio Municipal Lajeado",    "cidade": "Lajeado / RS",       "lat": -29.466, "lon": -51.961, "capacidade": 500,  "tipo": "Ginásio"},
    {"nome": "EEEF Presidente Vargas",       "cidade": "Canoas / RS",         "lat": -29.918, "lon": -51.183, "capacidade": 300,  "tipo": "Escola"},
    {"nome": "Rodoviária de Porto Alegre",   "cidade": "Porto Alegre / RS",   "lat": -30.035, "lon": -51.221, "capacidade": 800,  "tipo": "Terminal"},
    {"nome": "Parque Harmonia",              "cidade": "Porto Alegre / RS",   "lat": -30.030, "lon": -51.238, "capacidade": 1200, "tipo": "Parque"},
    # São Sebastião / SP (referência às chuvas de 2023)
    {"nome": "CEMADEN Abrigo Litoral Norte", "cidade": "São Sebastião / SP",  "lat": -23.808, "lon": -45.408, "capacidade": 400,  "tipo": "Centro de Apoio"},
    {"nome": "Ginásio Municipal Boiçucanga", "cidade": "São Sebastião / SP",  "lat": -23.780, "lon": -45.542, "capacidade": 250,  "tipo": "Ginásio"},
    # São Paulo - Capital
    {"nome": "Centro de Acolhida Bom Prato", "cidade": "São Paulo / SP",     "lat": -23.543, "lon": -46.634, "capacidade": 600,  "tipo": "Centro de Apoio"},
    {"nome": "Ginásio do Ibirapuera",        "cidade": "São Paulo / SP",      "lat": -23.587, "lon": -46.657, "capacidade": 2000, "tipo": "Ginásio"},
]
df_abrigos = pd.DataFrame(ABRIGOS)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

@st.cache_data(ttl=600)
def buscar_cotacoes():
    """Busca cotações em tempo real via Yahoo Finance (painel_ceo.py original)."""
    tickers = {
        "Brent (Petroleo)":  "BZ=F",
        "ExxonMobil (EUA)":  "XOM",
        "Chevron (EUA)":     "CVX",
        "Shell (Europa)":    "SHEL",
        "BP (Reino Unido)":  "BP",
        "Vale (Brasil)":     "VALE",
        "BHP (Australia)":   "BHP",
        "Rio Tinto (UK)":    "RIO",
        "Bunge (Agro)":      "BG",
        "Raízen (Brasil)":   "RAIZ4.SA",
    }
    precos = []
    for nome, t in tickers.items():
        try:
            ativo = yf.Ticker(t).history(period="1d")
            valor = ativo["Close"].iloc[-1]
            precos.append({"Empresa": nome, "Ticker": t,
                           "Cotacao Atual": f"US$ {valor:.2f}" if "RAIZ" not in t else f"R$ {valor:.2f}"})
        except Exception:
            precos.append({"Empresa": nome, "Ticker": t, "Cotacao Atual": "Mercado Fechado"})
    return pd.DataFrame(precos)


@st.cache_data(ttl=600)
def buscar_nasa():
    """
    ÚNICA chamada à API NASA EONET — compartilhada por todas as três visões.
    Inclui wildfires, severeStorms, earthquakes e floods (união das duas versões anteriores).
    """
    try:
        url = ("https://eonet.gsfc.nasa.gov/api/v3/events"
               "?status=open&category=wildfires,severeStorms,earthquakes,floods")
        return requests.get(url, timeout=10).json().get("events", [])
    except Exception:
        return []


def calcular_distancia(lat1, lon1, lat2, lon2):
    """Fórmula Haversine — intocada do painel_ceo.py original."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def gerar_recomendacao_ia_local(evento_nome, abrigo_nome, distancia_km):
    """
    IA de fallback embutida para a visão de Abrigos (omni_ecoresue_mvp.py original).
    Não depende de OCI nem de nuvem.
    """
    if distancia_km < 100:
        return (f"**🤖 IA Recomenda:** EVACUAÇÃO IMEDIATA! O evento '{evento_nome}' está a apenas "
                f"{distancia_km:.0f} km do abrigo **{abrigo_nome}**. "
                "Ative o protocolo de emergência e direcione as equipes de resgate agora.")
    elif distancia_km < 300:
        return (f"**🤖 IA Recomenda:** ALERTA LARANJA. '{evento_nome}' detectado a {distancia_km:.0f} km. "
                f"Prepare o abrigo **{abrigo_nome}** e monitore a evolução do evento a cada 30 minutos.")
    else:
        return (f"**🤖 IA Recomenda:** Monitoramento ativo. '{evento_nome}' está a {distancia_km:.0f} km. "
                "Sem necessidade de evacuação imediata, mas manter canais de comunicação abertos.")


# ============================================================
# CARREGAMENTO ANTECIPADO DOS DADOS (uma única vez por sessão)
# ============================================================
eventos_nasa = buscar_nasa()   # compartilhado pelas três visões
df_cotacoes  = buscar_cotacoes()

# ============================================================
# SIDEBAR: MENU DE NAVEGAÇÃO
# ============================================================
st.sidebar.title("🛡️ Omni-EcoRescue")
st.sidebar.markdown("*Tech4Change 2026 — Grupo 12*")
st.sidebar.markdown("---")

visao = st.sidebar.radio(
    "Selecione o Perfil de Usuário:",
    ["Corporativo (B2B)", "Impacto Social / ESG (Comunidade)", "Abrigos e Preparação", "RAG Vetorial (Histórico)"]
)

st.sidebar.markdown("---")
st.sidebar.info("⚡ Dados NASA em tempo real\n\n📡 IA: Oracle Cloud (OCI)")

modo_teste = st.sidebar.toggle("Modo de teste (simulação)", value=False)
if modo_teste and visao != "Abrigos e Preparação":
    eventos_nasa.insert(0, {
        "title": "Incêndio simulado",
        "categories": [{"title": "Wildfires"}],
        "geometry": [{"coordinates": [-87.0, 28.5]}]
    })


# ============================================================
# VISÃO 1: CORPORATIVO (B2B)  —  painel_ceo.py original intacto
# ============================================================
if visao == "Corporativo (B2B)":
    st.title("🌐 Omni-EcoRescue - DASHBOARD CORPORATIVO")
    st.markdown("Monitoramento Aeroespacial de Ativos de Petróleo, Mineração e Agronegócio")
    st.markdown("---")

    col_mapa, col_ia = st.columns([3, 1])

    with col_mapa:
        st.subheader("🛰️ Radares Espaciais NASA vs Infraestrutura Global")
        st.map(df_ativos, zoom=1, color="#00ff00")

        st.subheader("📈 Mercado Financeiro em Tempo Real (Yahoo Finance)")
        st.dataframe(df_cotacoes, width='stretch')

    with col_ia:
        st.subheader("🤖 Assistente de Risco Operacional")
        alerta_disparado = False
        for ativo in mapa_dados:
            for evento in eventos_nasa[:50]:
                try:
                    lon_nasa, lat_nasa = evento["geometry"][-1].get("coordinates")
                except (KeyError, IndexError, TypeError):
                    continue
                dist = calcular_distancia(ativo["lat"], ativo["lon"], lat_nasa, lon_nasa)
                if dist < 600:
                    alerta_disparado = True
                    if evento["title"] == "Incêndio simulado":
                        st.warning("SIMULAÇÃO: evento fictício, não é dado da NASA")
                    st.error("🚨 **PERIGO A ATIVOS DETECTADO**")
                    st.warning(f"**Gatilho:** {evento['title']}\n\n**Ativo:** {ativo['ativo']}\n\n**Distância:** {dist:.0f} KM")
                    st.markdown("### 🏭 ALERTA PATRIMONIAL")
                    texto_ia = gerar_recomendacao_rag(evento["title"], ativo["ativo"], dist, visao)
                    st.info(texto_ia)
                    if st.button("ENVIAR ORDEM DE BLOQUEIO", key="btn_corp_bloqueio"):
                        st.success("✅ Ordem de Bloqueio enviada para a central de operacoes.")
                    break
            if alerta_disparado:
                break
        if not alerta_disparado:
            st.success("✅ Nenhum ativo corporativo em risco.")


# ============================================================
# VISÃO 2: IMPACTO SOCIAL / ESG  —  painel_ceo.py original intacto
# ============================================================
elif visao == "Impacto Social / ESG (Comunidade)":
    st.title("🛡️ Omni-EcoRescue - CENTRO DE COMANDO ESG")
    st.markdown("Prevenção Humanitária, Epidemiológica e Ambiental Pós-Desastre")
    st.markdown("---")

    col_mapa, col_ia = st.columns([3, 1])

    with col_mapa:
        st.subheader("🌍 Radares Espaciais NASA vs Zonas de Vulnerabilidade")
        st.map(df_ativos, zoom=1, color="#ff0000")

    with col_ia:
        st.subheader("🤖 Assistente Humanitário (RAG)")
        alerta_disparado = False
        for ativo in mapa_dados:
            for evento in eventos_nasa[:50]:
                try:
                    lon_nasa, lat_nasa = evento["geometry"][-1].get("coordinates")
                except (KeyError, IndexError, TypeError):
                    continue
                dist = calcular_distancia(ativo["lat"], ativo["lon"], lat_nasa, lon_nasa)
                if dist < 600:
                    alerta_disparado = True
                    if evento["title"] == "Incêndio simulado":
                        st.warning("SIMULAÇÃO: evento fictício, não é dado da NASA")
                    st.error("🚨 **EMERGÊNCIA SOCIAL DETECTADA**")
                    st.warning(f"**Desastre:** {evento['title']}\n\n**Zona Afetada:** Raio de {dist:.0f} KM do complexo industrial.")
                    st.markdown("### 🚑 PLANO DE SAÚDE PÚBLICA")
                    st.error(f"**Comunidade Ameaçada:** {ativo['comunidade_vizinha']}\n\n**Risco Secundário:** {ativo['risco_secundario']}")
                    texto_ia = gerar_recomendacao_rag(evento["title"], ativo["ativo"], dist, visao)
                    st.info(texto_ia)
                    if st.button("ACIONAR LIDERANÇAS E ONGS", key="btn_esg_ongs"):
                        st.success("✅ Protocolos enviados para Associações Locais e ONGs.")
                    break
            if alerta_disparado:
                break
        if not alerta_disparado:
            st.success("✅ Nenhuma comunidade em risco crítico.")


# ============================================================
# VISÃO 3: ABRIGOS E PREPARAÇÃO  —  omni_ecoresue_mvp.py original intacto
# ============================================================
elif visao == "Abrigos e Preparação":
    st.title("🏠 Abrigos e Preparação para Desastres")
    st.markdown("Localize abrigos de evacuação, monitore alertas NASA e verifique seu nível de preparo.")
    st.markdown("---")

    aba1, aba2, aba3 = st.tabs(["🗺️ Mapa de Abrigos", "🚨 Central de Alertas", "✅ Checklist de Sobrevivência"])

    # ----------------------------------------------------------
    # ABA 1: MAPA DE ABRIGOS
    # ----------------------------------------------------------
    with aba1:
        cidade_sel = st.selectbox(
            "📍 Onde você está?",
            ["São Paulo/SP", "São Sebastião/SP", "Porto Alegre/RS", "Lajeado/RS", "Macaé/RJ"],
            key="sel_cidade_mapa",
            help="Define o centro do mapa e a posição inicial 'Você está aqui'."
        )
        render_mapa_interativo(ABRIGOS, eventos_nasa, origem=cidade_sel, altura=630)
        st.caption(
            "ℹ️ **Nota:** os locais (hospitais, UBS/UPA, farmácias, mercados, hotéis etc.) são buscados no OpenStreetMap; se a busca falhar, entra uma lista de reserva ilustrativa. Os abrigos são cadastrados no MVP, com coordenadas aproximadas. Ao clicar em um ponto, a rota abre no Waze ou no Google Maps, a partir do ponto azul."
        )



    # ----------------------------------------------------------
    # ABA 2: CENTRAL DE ALERTAS (usa eventos_nasa já carregados)
    # ----------------------------------------------------------
    with aba2:
        st.subheader("🚨 Central de Alertas — NASA EONET ao Vivo")
        st.markdown("Cruzamento de desastres naturais em tempo real com os abrigos cadastrados.")

        if not eventos_nasa:
            st.warning("⚠️ Não foi possível conectar à NASA no momento. Verifique sua conexão com a internet.")
        else:
            st.success(f"✅ NASA conectada! **{len(eventos_nasa)} eventos ativos** detectados no planeta agora.")
            st.markdown("---")

            alertas_gerados = []
            for abrigo in ABRIGOS:
                for evento in eventos_nasa[:50]:
                    try:
                        coords = evento["geometry"][-1].get("coordinates")
                        if not coords:
                            continue
                        lon_nasa, lat_nasa = coords[0], coords[1]
                        dist = calcular_distancia(abrigo["lat"], abrigo["lon"], lat_nasa, lon_nasa)
                        if dist < 600:
                            alertas_gerados.append({
                                "abrigo":       abrigo["nome"],
                                "cidade":       abrigo["cidade"],
                                "evento_nasa":  evento["title"],
                                "distancia_km": dist,
                                "recomendacao": gerar_recomendacao_ia_local(evento["title"], abrigo["nome"], dist),
                            })
                            break
                    except (KeyError, IndexError, TypeError):
                        continue

            if alertas_gerados:
                alertas_gerados.sort(key=lambda x: x["distancia_km"])
                for alerta in alertas_gerados:
                    nivel = "🔴" if alerta["distancia_km"] < 100 else "🟡" if alerta["distancia_km"] < 300 else "🟢"
                    with st.expander(f"{nivel} {alerta['evento_nasa']} — {alerta['distancia_km']:.0f} km de {alerta['cidade']}"):
                        st.error(f"🏠 **Abrigo em risco:** {alerta['abrigo']}")
                        st.warning(f"🌪️ **Evento NASA:** {alerta['evento_nasa']}\n\n📏 **Distância:** {alerta['distancia_km']:.0f} km")
                        st.info(alerta["recomendacao"])
                        if st.button(f"🚁 Acionar Resgate — {alerta['abrigo'][:30]}", key=f"resgate_{alerta['abrigo']}"):
                            st.success("✅ Equipes de resgate notificadas! Protocolo de evacuação iniciado.")
            else:
                st.success("✅ Nenhum abrigo em risco crítico no momento. Monitoramento ativo.")

            st.markdown("---")
            st.subheader("📋 Últimos Eventos NASA Detectados")
            dados_tabela = []
            for ev in eventos_nasa[:10]:
                try:
                    coords = ev["geometry"][-1].get("coordinates", ["-", "-"])
                    dados_tabela.append({
                        "Evento":    ev.get("title", "?"),
                        "Categoria": ev["categories"][0]["title"] if ev.get("categories") else "?",
                        "Lon":       coords[0],
                        "Lat":       coords[1],
                    })
                except (KeyError, IndexError):
                    continue
            if dados_tabela:
                st.dataframe(pd.DataFrame(dados_tabela), width='stretch')

    # ----------------------------------------------------------
    # ABA 3: CHECKLIST DE SOBREVIVÊNCIA
    # ----------------------------------------------------------
    with aba3:
        st.subheader("✅ Checklist de Sobrevivência")
        st.markdown("Prepare-se antes que o desastre aconteça. "
                    "A **Regra dos 30 segundos**: quando o alerta soa, você não tem tempo para pensar, só para agir.")
        st.markdown("---")

        st.subheader("🎒 Mochila de Emergência — O que você já tem pronto?")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💧 Água e Alimentação**")
            agua      = st.checkbox("💧 Água potável (mín. 3 litros por pessoa/dia)")
            alimentos = st.checkbox("🥫 Alimentos não-perecíveis (enlatados, barras energéticas)")
            abridor   = st.checkbox("🔧 Abridor de latas manual")

            st.markdown("**💊 Saúde e Primeiros Socorros**")
            kit_medico = st.checkbox("🩺 Kit de primeiros socorros (curativo, antisséptico)")
            remedios   = st.checkbox("💊 Medicamentos pessoais (para ao menos 7 dias)")
            mascara    = st.checkbox("😷 Máscaras de proteção")

        with col2:
            st.markdown("**📄 Documentos e Comunicação**")
            documentos = st.checkbox("📄 Documentos em saco plástico (RG, CPF, cartão SUS)")
            celular    = st.checkbox("📱 Celular carregado + carregador portátil")
            radio      = st.checkbox("📻 Rádio a pilha para receber alertas sem internet")
            dinheiro   = st.checkbox("💵 Dinheiro em espécie (mínimo R$ 200)")

            st.markdown("**🔦 Segurança e Mobilidade**")
            lanterna = st.checkbox("🔦 Lanterna com pilhas reserva")
            apito    = st.checkbox("🔔 Apito (para pedir socorro se ficar preso)")
            calcado  = st.checkbox("👟 Calçado fechado e resistente")
            agasalho = st.checkbox("🧥 Agasalho e cobertor")

        itens    = [agua, alimentos, abridor, kit_medico, remedios, mascara,
                    documentos, celular, radio, dinheiro, lanterna, apito, calcado, agasalho]
        total    = len(itens)
        marcados = sum(itens)
        pct      = int((marcados / total) * 100)

        st.markdown("---")
        st.subheader(f"📊 Seu nível de preparação: {pct}%")
        st.progress(pct / 100)

        if pct == 100:
            st.success("🏆 **PARABÉNS!** Você está 100% preparado. Sua família está protegida!")
        elif pct >= 70:
            st.warning(f"⚠️ Bom nível! Você tem {marcados} de {total} itens. Complete os que faltam o quanto antes.")
        elif pct >= 40:
            st.warning(f"🟡 Atenção! Apenas {marcados} de {total} itens prontos. Priorize água, documentos e medicamentos.")
        else:
            st.error(f"🔴 **RISCO ALTO!** Apenas {marcados} de {total} itens. Monte sua mochila de emergência hoje!")

        st.markdown("---")
        st.subheader("📞 Contatos de Emergência Brasil")
        contatos = {
            "🚨 Defesa Civil":             "199",
            "🚒 Bombeiros":                "193",
            "🚑 SAMU":                     "192",
            "👮 Polícia Militar":           "190",
            "💧 INMET (Alertas Climáticos)":"0800 610 217",
        }
        for nome_c, numero in contatos.items():
            st.markdown(f"- **{nome_c}:** `{numero}`")

        st.markdown("---")
        st.info("💡 **Dica:** Salve esses números no seu celular agora. Em uma emergência, cada segundo conta.")

# ============================================================
# VISÃO 4: RAG VETORIAL (Histórico)
# ============================================================
elif visao == "RAG Vetorial (Histórico)":
    import chromadb
    from chromadb.utils import embedding_functions

    st.title("📚 RAG Vetorial: Histórico de Desastres")
    st.markdown("Busca semântica avançada nos relatórios passados da Defesa Civil.")
    st.markdown("---")

    # Puxa a chave do secrets do Streamlit
    try:
        COHERE_API_KEY = st.secrets["oci"]["COHERE_API_KEY"]
    except KeyError:
        st.error("Chave COHERE_API_KEY não encontrada no secrets.toml!")
        st.stop()

    st.write("🤖 Iniciando Banco de Dados Vetorial (ChromaDB)...")

    # Inicia o ChromaDB local
    chroma_client = chromadb.PersistentClient(path="./banco_historico")

    # Configura o modelo de Embeddings da Cohere
    cohere_ef = embedding_functions.CohereEmbeddingFunction(
        api_key=COHERE_API_KEY,
        model_name="embed-multilingual-v3.0"
    )

    # Cria a coleção
    colecao = chroma_client.get_or_create_collection(
        name="relatorios_defesa_civil",
        embedding_function=cohere_ef
    )

    st.success("✅ Banco Vetorial conectado com sucesso!")

    # Fase de INGESTÃO
    with st.expander("📥 Ver Documentos Históricos (Arquivos Base)"):
        documentos_historicos = [
            "Relatório 2024 (Enchentes no RS): A evacuação deve começar 48h antes nas áreas de vale. Aprendizado: Faltou água potável e energia no abrigo central nas primeiras 12h.",
            "Relatório 2019 (Brumadinho): O rompimento de barragem revelou que sirenes terrestres podem falhar se a lama atingir a fiação. O uso de SMS foi mais eficaz na zona rural.",
            "Relatório 2023 (Incêndios no Pantanal): Os abrigos improvisados sofreram com a fumaça tóxica. É obrigatório instalar purificadores de ar nas tendas médicas."
        ]
        metadados = [{"evento": "enchente_rs"}, {"evento": "rompimento_barragem"}, {"evento": "incendio_pantanal"}]
        ids = ["doc1", "doc2", "doc3"]
        
        if colecao.count() == 0:
            colecao.add(documents=documentos_historicos, metadatas=metadados, ids=ids)
            st.write("*(Documentos inseridos no banco vetorial agora!)*")
        else:
            st.write(f"*(O banco já contém {colecao.count()} relatórios indexados).*")
            
        for doc in documentos_historicos:
            st.info(doc)

    # Fase de INFERÊNCIA (RAG)
    st.subheader("🔍 Nova Consulta ao Histórico")
    novo_desastre = st.text_input("Simulador de Alerta (O que a NASA acabou de detectar?):", "Risco altíssimo de fortes chuvas, inundações e enchentes detectado na região sul.")

    if st.button("Buscar Lições Aprendidas no Banco"):
        with st.spinner("Transformando texto em vetores e buscando no banco matemático..."):
            resultados = colecao.query(
                query_texts=[novo_desastre],
                n_results=1
            )
            
            st.warning("🚨 CONTEXTO RECUPERADO (Baseado na similaridade semântica)")
            st.write(resultados['documents'][0][0])

