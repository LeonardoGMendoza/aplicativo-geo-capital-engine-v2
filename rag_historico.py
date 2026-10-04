import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

st.set_page_config(page_title="RAG Histórico - Defesa Civil", page_icon="📚")
st.title("📚 RAG Vetorial: Histórico de Desastres")

# Puxa a chave do secrets do Streamlit
try:
    COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
except KeyError:
    st.error("Chave COHERE_API_KEY não encontrada no secrets.toml!")
    st.stop()

st.write("🤖 Iniciando Banco de Dados Vetorial (ChromaDB)...")

# Inicia o ChromaDB local (vai criar uma pasta ./banco_historico)
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

# ==========================================
# Fase de INGESTÃO
# ==========================================
with st.expander("📥 Ver Documentos Históricos (Arquivos Base)"):
    documentos_historicos = [
        "Relatório 2024 (Enchentes no RS): A evacuação deve começar 48h antes nas áreas de vale. Aprendizado: Faltou água potável e energia no abrigo central nas primeiras 12h.",
        "Relatório 2019 (Brumadinho): O rompimento de barragem revelou que sirenes terrestres podem falhar se a lama atingir a fiação. O uso de SMS foi mais eficaz na zona rural.",
        "Relatório 2023 (Incêndios no Pantanal): Os abrigos improvisados sofreram com a fumaça tóxica. É obrigatório instalar purificadores de ar nas tendas médicas."
    ]
    metadados = [{"evento": "enchente_rs"}, {"evento": "rompimento_barragem"}, {"evento": "incendio_pantanal"}]
    ids = ["doc1", "doc2", "doc3"]
    
    # Só adiciona se o banco estiver vazio para não duplicar toda vez que recarregar a tela
    if colecao.count() == 0:
        colecao.add(documents=documentos_historicos, metadatas=metadados, ids=ids)
        st.write("*(Documentos inseridos no banco vetorial agora!)*")
    else:
        st.write(f"*(O banco já contém {colecao.count()} relatórios indexados).*")
        
    for doc in documentos_historicos:
        st.info(doc)

# ==========================================
# Fase de INFERÊNCIA (RAG)
# ==========================================
st.subheader("🔍 Nova Consulta ao Histórico")
novo_desastre = st.text_input("Simulador de Alerta (O que a NASA acabou de detectar?):", "Risco altíssimo de fortes chuvas, inundações e enchentes detectado na região sul.")

if st.button("Buscar Lições Aprendidas no Banco"):
    with st.spinner("Transformando texto em vetores e buscando no banco matemático..."):
        # O RAG faz a Busca Semântica
        resultados = colecao.query(
            query_texts=[novo_desastre],
            n_results=1
        )
        
        st.warning("🚨 CONTEXTO RECUPERADO (Baseado na similaridade semântica)")
        st.write(resultados['documents'][0][0])
