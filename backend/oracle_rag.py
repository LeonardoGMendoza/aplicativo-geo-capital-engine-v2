import os
import oci
import streamlit as st


# O parametro _config comeca com "_" de proposito: o Streamlit nao o inclui na
# chave do cache, entao a chave privada nao fica indexada em memoria.
# Se a chamada falhar, a excecao sobe e NADA e guardado no cache.
@st.cache_data(ttl=600)
def _chamar_oracle_rag_cache(_config, compartment_id, prompt_sistema):
    genai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=_config)

    chat_request = oci.generative_ai_inference.models.CohereChatRequest(
        message=prompt_sistema,
        max_tokens=200,
        temperature=0.3
    )

    chat_detail = oci.generative_ai_inference.models.ChatDetails(
        compartment_id=compartment_id,
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
            model_id="cohere.command-a-03-2025"
        ),
        chat_request=chat_request
    )

    response = genai_client.chat(chat_detail)
    return response.data.chat_response.text


import chromadb
from chromadb.utils import embedding_functions

DOCUMENTOS_DEMO = [
    "Exemplo de demonstração (cenário de enchente): iniciar a evacuação com antecedência nas áreas de vale e garantir água potável e energia no abrigo central desde as primeiras horas.",
    "Exemplo de demonstração (cenário de rompimento de barragem): sirenes terrestres podem falhar; usar também alerta por SMS, principalmente em zona rural.",
    "Exemplo de demonstração (cenário de incêndio): abrigos e tendas médicas precisam de proteção contra fumaça, como purificadores de ar."
]

METADADOS_DEMO = [{"evento": "enchente_rs"}, {"evento": "rompimento_barragem"}, {"evento": "incendio_pantanal"}]

def obter_colecao():
    if "oci" in st.secrets and "COHERE_API_KEY" in st.secrets["oci"]:
        COHERE_API_KEY = st.secrets["oci"]["COHERE_API_KEY"]
    else:
        raise KeyError("COHERE_API_KEY não encontrada")
    
    chroma_client = chromadb.PersistentClient(path="./banco_historico")
    cohere_ef = embedding_functions.CohereEmbeddingFunction(
        api_key=COHERE_API_KEY,
        model_name="embed-multilingual-v3.0"
    )
    colecao = chroma_client.get_or_create_collection(
        name="exemplos_demonstracao",
        embedding_function=cohere_ef,
        metadata={"hnsw:space": "cosine"}
    )
    if colecao.count() == 0:
        ids = [f"doc{i}" for i in range(len(DOCUMENTOS_DEMO))]
        colecao.add(documents=DOCUMENTOS_DEMO, metadatas=METADADOS_DEMO, ids=ids)
    return colecao

@st.cache_data(ttl=600)
def _consultar_historico_cache(evento_nome):
    colecao = obter_colecao()
    resultados = colecao.query(query_texts=[evento_nome], n_results=1)
    if resultados['documents'] and len(resultados['documents'][0]) > 0:
        return resultados['documents'][0][0]
    return "Sem dados históricos."

def gerar_recomendacao_rag(evento_nome, ativo_nome, distancia, visao):
    
    # ==========================================
    # RECUPERAÇÃO DO BANCO VETORIAL (O "R" DO RAG)
    # ==========================================
    contexto_historico = "Sem dados históricos."
    try:
        contexto_historico = _consultar_historico_cache(evento_nome)
    except Exception as e:
        print(f"[RAG] Erro ao buscar no banco vetorial: {e}")

    # ==========================================
    # CONSTRUÇÃO DO PROMPT (O "A" DO RAG)
    # ==========================================
    prompt_sistema = f"""
    Você é a IA de tomada de decisão do Omni-EcoRescue.

    DADOS DO EVENTO ATUAL (TEMPO REAL NASA):
    - Desastre: {evento_nome}
    - Infraestrutura em risco: {ativo_nome}
    - Distância: {distancia:.0f} KM
    - Perfil Solicitante: {visao}

    EXEMPLO HISTÓRICO DE DEMONSTRAÇÃO (RECUPERADO VIA BANCO VETORIAL):
    "{contexto_historico}"

    INSTRUÇÃO:
    Você deve formular uma recomendação estratégica. Utilize o exemplo histórico de demonstração para orientar a recomendação.
    Se o perfil for "Corporativo (B2B)", foque na mitigação de risco patrimonial.
    Se o perfil for "Impacto Social / ESG", foque na evacuação e saúde pública.
    Limite a 2 ou 3 frases curtas. Inicie com "**Decisão RAG (IA):**".
    """

    try:
        config = None
        compartment_id = None

        # (a) Tenta st.secrets (arquivo .streamlit/secrets.toml, secao [oci])
        try:
            if "oci" in st.secrets:
                s = st.secrets["oci"]
                config = {
                    "user": s["user"],
                    "fingerprint": s["fingerprint"],
                    "tenancy": s["tenancy"],
                    "region": s["region"],
                    "key_content": s["key_content"],
                }
                compartment_id = s.get("compartment_id") or os.environ.get("OCI_COMPARTMENT_ID")
        except FileNotFoundError:
            pass  # Nao tem secrets.toml, segue para o modo local
        except KeyError as e:
            # Secrets existe, mas falta um campo. Loga so o NOME do campo, nunca o valor.
            print(f"[Oracle RAG] secrets [oci] incompleto: falta o campo {e}")
            config = None
        except Exception as e:
            print(f"[Oracle RAG] erro ao ler secrets ({type(e).__name__})")
            config = None

        # (b) Se nao achou em secrets, tenta o arquivo local ~/.oci/config
        if not config:
            config = oci.config.from_file()
            compartment_id = os.environ.get("OCI_COMPARTMENT_ID")

        if not compartment_id:
            raise ValueError("compartment_id nao encontrado em st.secrets nem na variavel de ambiente.")

        # Valida a config
        oci.config.validate_config(config)

        # Chama a funcao com cache (so respostas reais ficam em cache)
        resposta_oracle = _chamar_oracle_rag_cache(config, compartment_id, prompt_sistema)
        return "**Decisão RAG (IA):** " + resposta_oracle.replace("**Decisão RAG (IA):**", "").strip()

    except Exception as e:
        # Loga so o tipo do erro e uma mensagem curta, sem valores de credencial
        tipo_erro = type(e).__name__
        msg_curta = str(e).split("\n")[0][:60]
        print(f"[Oracle RAG] Fallback ativado ({tipo_erro}: {msg_curta})")

        if visao == "Corporativo (B2B)":
            return "**Modo seguro (texto local):** Interromper operação. O valor atual das ações no mercado amortiza perdas. Evitando dano estrutural bilionário."
        else:
            return "**Modo seguro (texto local):** Enviar kits de descontaminação e água potável. Acionar resgate humanitário prioritário para grupos vulneráveis."