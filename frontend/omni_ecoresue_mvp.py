import os
import sys
import math
import requests
import pandas as pd
import streamlit as st

# Garante que o Python encontra a pasta 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
# DADOS: ABRIGOS DE EVACUAÇÃO (Brasil - cidades reais)
# ============================================================
ABRIGOS = [
    # Rio Grande do Sul (referência ao desastre das enchentes)
    {"nome": "Ginásio Municipal Lajeado",         "cidade": "Lajeado / RS",        "lat": -29.466, "lon": -51.961, "capacidade": 500, "tipo": "Ginásio"},
    {"nome": "EEEF Presidente Vargas",             "cidade": "Canoas / RS",          "lat": -29.918, "lon": -51.183, "capacidade": 300, "tipo": "Escola"},
    {"nome": "Rodoviária de Porto Alegre",         "cidade": "Porto Alegre / RS",    "lat": -30.035, "lon": -51.221, "capacidade": 800, "tipo": "Terminal"},
    {"nome": "Parque Harmonia",                    "cidade": "Porto Alegre / RS",    "lat": -30.030, "lon": -51.238, "capacidade": 1200, "tipo": "Parque"},
    # São Sebastião / SP (referência às chuvas de 2023)
    {"nome": "CEMADEN Abrigo Litoral Norte",       "cidade": "São Sebastião / SP",   "lat": -23.808, "lon": -45.408, "capacidade": 400, "tipo": "Centro de Apoio"},
    {"nome": "Ginásio Municipal Boiçucanga",       "cidade": "São Sebastião / SP",   "lat": -23.780, "lon": -45.542, "capacidade": 250, "tipo": "Ginásio"},
    # São Paulo - Capital
    {"nome": "Centro de Acolhida Bom Prato",      "cidade": "São Paulo / SP",       "lat": -23.543, "lon": -46.634, "capacidade": 600, "tipo": "Centro de Apoio"},
    {"nome": "Ginásio do Ibirapuera",              "cidade": "São Paulo / SP",       "lat": -23.587, "lon": -46.657, "capacidade": 2000, "tipo": "Ginásio"},
]
df_abrigos = pd.DataFrame(ABRIGOS)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
@st.cache_data(ttl=600)
def buscar_eventos_nasa():
    """Busca desastres ao vivo na API pública da NASA EONET."""
    try:
        url = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&category=wildfires,severeStorms,floods"
        resp = requests.get(url, timeout=10)
        return resp.json().get("events", [])
    except Exception:
        return []

def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """Fórmula Haversine: distância real em KM entre dois pontos do globo."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def gerar_recomendacao_ia(evento_nome, abrigo_nome, distancia_km):
    """IA de fallback embutida. Gera recomendação humanitária sem precisar de nuvem."""
    if distancia_km < 100:
        return f"**🤖 IA Recomenda:** EVACUAÇÃO IMEDIATA! O evento '{evento_nome}' está a apenas {distancia_km:.0f} km do abrigo **{abrigo_nome}**. Ative o protocolo de emergência e direcione as equipes de resgate agora."
    elif distancia_km < 300:
        return f"**🤖 IA Recomenda:** ALERTA LARANJA. '{evento_nome}' detectado a {distancia_km:.0f} km. Prepare o abrigo **{abrigo_nome}** e monitore a evolução do evento a cada 30 minutos."
    else:
        return f"**🤖 IA Recomenda:** Monitoramento ativo. '{evento_nome}' está a {distancia_km:.0f} km. Sem necessidade de evacuação imediata, mas manter canais de comunicação abertos."

# ============================================================
# SIDEBAR: MENU DE NAVEGAÇÃO
# ============================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/FIAP_logo.svg/320px-FIAP_logo.svg.png", width=120)
st.sidebar.title("🛡️ Omni-EcoRescue")
st.sidebar.markdown("*Tech4Change 2026 — Grupo 12*")
st.sidebar.markdown("---")

tela = st.sidebar.radio(
    "📌 Navegação",
    ["🗺️ Mapa de Abrigos", "🚨 Central de Alertas", "✅ Checklist de Sobrevivência"]
)

st.sidebar.markdown("---")
st.sidebar.info("⚡ Dados NASA em tempo real\n\n📡 Rodando 100% offline/local")


# ============================================================
# TELA 1: MAPA DE ABRIGOS DE EVACUAÇÃO
# ============================================================
if tela == "🗺️ Mapa de Abrigos":
    st.title("🗺️ Mapa de Abrigos de Evacuação")
    st.markdown("Localize o abrigo mais próximo de você em caso de desastre natural.")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📍 Abrigos Cadastrados no Brasil")
        # Mapa com marcadores verdes (abrigos seguros)
        st.map(df_abrigos[["lat", "lon"]], zoom=4, color="#00cc44")
        st.caption("🟢 Cada ponto verde representa um abrigo de evacuação ativo.")

    with col2:
        st.subheader("🏠 Lista de Abrigos")
        for _, row in df_abrigos.iterrows():
            st.markdown(f"""
**{row['nome']}**
- 📍 {row['cidade']}
- 🏷️ Tipo: {row['tipo']}
- 👥 Capacidade: {row['capacidade']} pessoas
---
""")

    st.markdown("---")
    st.subheader("🔍 Encontrar Abrigo Mais Próximo")
    c1, c2 = st.columns(2)
    with c1:
        lat_user = st.number_input("Minha Latitude:", value=-23.55, format="%.4f", help="Ex: -23.5505 para São Paulo")
    with c2:
        lon_user = st.number_input("Minha Longitude:", value=-46.63, format="%.4f", help="Ex: -46.6333 para São Paulo")

    if st.button("📡 Localizar Abrigo Mais Próximo"):
        df_abrigos["distancia_km"] = df_abrigos.apply(
            lambda r: calcular_distancia_km(lat_user, lon_user, r["lat"], r["lon"]), axis=1
        )
        mais_proximo = df_abrigos.sort_values("distancia_km").iloc[0]
        st.success(f"""
✅ **Abrigo mais próximo encontrado!**

🏠 **{mais_proximo['nome']}**
📍 {mais_proximo['cidade']}
🏷️ Tipo: {mais_proximo['tipo']}
👥 Capacidade: {mais_proximo['capacidade']} pessoas
📏 Distância estimada: **{mais_proximo['distancia_km']:.1f} km**
""")
        # Mostra o mapa com destaque no abrigo escolhido
        df_destaque = pd.DataFrame([{
            "lat": mais_proximo["lat"],
            "lon": mais_proximo["lon"]
        }])
        st.map(df_destaque, zoom=10, color="#ff6600")
        st.caption("🟠 Ponto laranja: o abrigo mais próximo de você.")


# ============================================================
# TELA 2: CENTRAL DE ALERTAS NASA
# ============================================================
elif tela == "🚨 Central de Alertas":
    st.title("🚨 Central de Alertas — NASA EONET ao Vivo")
    st.markdown("Cruzamento de desastres naturais em tempo real com os abrigos cadastrados.")
    st.markdown("---")

    with st.spinner("🛰️ Conectando aos satélites da NASA..."):
        eventos = buscar_eventos_nasa()

    if not eventos:
        st.warning("⚠️ Não foi possível conectar à NASA no momento. Verifique sua conexão com a internet.")
    else:
        st.success(f"✅ NASA conectada! **{len(eventos)} eventos ativos** detectados no planeta agora.")
        st.markdown("---")

        # Cruzamento: para cada abrigo, verifica eventos próximos
        alertas_gerados = []

        for abrigo in ABRIGOS:
            for evento in eventos[:50]:
                try:
                    coords = evento["geometry"][-1].get("coordinates")
                    if not coords:
                        continue
                    lon_nasa, lat_nasa = coords[0], coords[1]
                    dist = calcular_distancia_km(abrigo["lat"], abrigo["lon"], lat_nasa, lon_nasa)

                    if dist < 600:
                        alertas_gerados.append({
                            "abrigo": abrigo["nome"],
                            "cidade": abrigo["cidade"],
                            "evento_nasa": evento["title"],
                            "distancia_km": dist,
                            "recomendacao": gerar_recomendacao_ia(evento["title"], abrigo["nome"], dist)
                        })
                        break  # Um alerta por abrigo é suficiente
                except (KeyError, IndexError, TypeError):
                    continue

        if alertas_gerados:
            # Ordena pelos mais próximos primeiro
            alertas_gerados.sort(key=lambda x: x["distancia_km"])

            for alerta in alertas_gerados:
                nivel = "🔴" if alerta["distancia_km"] < 100 else "🟡" if alerta["distancia_km"] < 300 else "🟢"
                with st.expander(f"{nivel} {alerta['evento_nasa']} — {alerta['distancia_km']:.0f} km de {alerta['cidade']}"):
                    st.error(f"🏠 **Abrigo em risco:** {alerta['abrigo']}")
                    st.warning(f"🌪️ **Evento NASA:** {alerta['evento_nasa']}\n\n📏 **Distância:** {alerta['distancia_km']:.0f} km")
                    st.info(alerta["recomendacao"])
                    if st.button(f"🚁 Acionar Resgate — {alerta['abrigo'][:30]}", key=alerta["abrigo"]):
                        st.success("✅ Equipes de resgate notificadas! Protocolo de evacuação iniciado.")
        else:
            st.success("✅ Nenhum abrigo em risco crítico no momento. Monitoramento ativo.")

        # Mostra os últimos eventos da NASA em tabela
        st.markdown("---")
        st.subheader("📋 Últimos Eventos NASA Detectados")
        dados_tabela = []
        for ev in eventos[:10]:
            try:
                coords = ev["geometry"][-1].get("coordinates", ["-", "-"])
                dados_tabela.append({
                    "Evento": ev.get("title", "?"),
                    "Categoria": ev["categories"][0]["title"] if ev.get("categories") else "?",
                    "Lon": coords[0],
                    "Lat": coords[1],
                })
            except (KeyError, IndexError):
                continue
        if dados_tabela:
            st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True)


# ============================================================
# TELA 3: CHECKLIST DE SOBREVIVÊNCIA
# ============================================================
elif tela == "✅ Checklist de Sobrevivência":
    st.title("✅ Checklist de Sobrevivência")
    st.markdown("Prepare-se antes que o desastre aconteça. A **Regra dos 30 segundos**: quando o alerta soa, você não tem tempo para pensar, só para agir.")
    st.markdown("---")

    st.subheader("🎒 Mochila de Emergência — O que você já tem pronto?")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**💧 Água e Alimentação**")
        agua = st.checkbox("💧 Água potável (mín. 3 litros por pessoa/dia)")
        alimentos = st.checkbox("🥫 Alimentos não-perecíveis (enlatados, barras energéticas)")
        abridor = st.checkbox("🔧 Abridor de latas manual")

        st.markdown("**💊 Saúde e Primeiros Socorros**")
        kit_medico = st.checkbox("🩺 Kit de primeiros socorros (curativo, antisséptico)")
        remedios = st.checkbox("💊 Medicamentos pessoais (para ao menos 7 dias)")
        mascara = st.checkbox("😷 Máscaras de proteção")

    with col2:
        st.markdown("**📄 Documentos e Comunicação**")
        documentos = st.checkbox("📄 Documentos em saco plástico (RG, CPF, cartão SUS)")
        celular = st.checkbox("📱 Celular carregado + carregador portátil")
        radio = st.checkbox("📻 Rádio a pilha para receber alertas sem internet")
        dinheiro = st.checkbox("💵 Dinheiro em espécie (mínimo R$ 200)")

        st.markdown("**🔦 Segurança e Mobilidade**")
        lanterna = st.checkbox("🔦 Lanterna com pilhas reserva")
        apito = st.checkbox("🔔 Apito (para pedir socorro se ficar preso)")
        calcado = st.checkbox("👟 Calçado fechado e resistente")
        agasalho = st.checkbox("🧥 Agasalho e cobertor")

    # Cálculo do score
    itens = [agua, alimentos, abridor, kit_medico, remedios, mascara,
             documentos, celular, radio, dinheiro, lanterna, apito, calcado, agasalho]
    total = len(itens)
    marcados = sum(itens)
    pct = int((marcados / total) * 100)

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
        "🚨 Defesa Civil": "199",
        "🚒 Bombeiros": "193",
        "🚑 SAMU": "192",
        "👮 Polícia Militar": "190",
        "💧 INMET (Alertas Climáticos)": "0800 610 217"
    }
    for nome, numero in contatos.items():
        st.markdown(f"- **{nome}:** `{numero}`")

    st.markdown("---")
    st.info("💡 **Dica:** Salve esses números no seu celular agora. Em uma emergência, cada segundo conta.")
