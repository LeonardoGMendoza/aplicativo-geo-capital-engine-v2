# Omni-EcoRescue
**Acesso ao MVP Público:** [https://aplicativo-geo-capital-engine-3k7pun8ggkjwsyvgb2pgvm.streamlit.app/](https://aplicativo-geo-capital-engine-3k7pun8ggkjwsyvgb2pgvm.streamlit.app/)

Sistema preditivo que cruza dados de desastres da NASA com ativos industriais globais (plataformas offshore, mineração, agronegócio) para prevenir perdas corporativas e proteger comunidades vizinhas em risco.

Projeto desenvolvido para o Hackathon "Tech for Change".

---

## O Problema

Desastres climáticos severos atingem infraestruturas industriais críticas. A falta de precisão na tomada de decisão gera duas consequências:

- **Dano Corporativo**: perda estrutural e desvalorização de ativos.
- **Dano Social**: comunidades vizinhas (pescadores, ribeirinhos) afetadas por riscos secundários (vazamentos, contaminação) sem tempo hábil para evacuação.

## A Solução

Painel com três visões. As duas primeiras apresentam, para o mesmo evento de risco, duas perspectivas:

- **Visão Corporativa (B2B)**: cruza a localização do evento (NASA EONET) com o valor de mercado do ativo (Yahoo Finance) e recomenda ação de mitigação.
- **Visão de Impacto Social (ESG/Comunidade)**: identifica a comunidade vizinha ao ativo e recomenda protocolo de evacuação/suporte humanitário.

- **Abrigos e Preparação (Comunidade)**: mapa interativo para localizar abrigos de evacuação e serviços essenciais próximos (hospitais, UBS/UPA, delegacias, ONGs, farmácias, mercados, alimentação e hospedagem), com alertas NASA e checklist de sobrevivência.

Nas visões Corporativa e ESG, o sistema recomenda — a decisão final e o acionamento de qualquer ação são sempre confirmados por um humano, via botão no painel (Human-in-the-Loop).

## Estudo de Caso

Bacia de Campos (RJ) — infraestrutura da Petrobras e Colônia de Pescadores Z3 de Macaé, que já possui vínculo formal com a Petrobras via Plano de Compensação Ambiental exigido pelo IBAMA.

## Arquitetura

| Camada | Tecnologia |
|---|---|
| Frontend | Streamlit (`frontend/painel_ceo.py`) |
| Cálculo de risco geoespacial | `math` (fórmula de Haversine, raio de 600 km) |
| Dados de desastres | NASA EONET (tempo real) |
| Dados de mercado | Yahoo Finance (`yfinance`) |
| Mapa de abrigos | Leaflet (`frontend/mapa_interativo.py`) com locais do OpenStreetMap via Overpass API e busca de cidade via Nominatim |
| Rotas | Link para Waze ou Google Maps, partindo do ponto "você está aqui" |
| Inteligência Artificial | Oracle OCI Generative AI (`cohere.command-a-03-2025`), com fallback local seguro |

### Fluxo do sistema

```mermaid
flowchart TD
    A[NASA EONET<br/>eventos de desastre em tempo real] --> C{Cálculo de risco<br/>fórmula de Haversine<br/>raio 600 km}
    B[Yahoo Finance<br/>yfinance] --> C
    C --> D[Streamlit<br/>frontend/painel_ceo.py]
    D --> E[Motor de recomendação<br/>backend/oracle_rag.py]
    E -->|credencial OCI configurada| F[Oracle OCI GenAI<br/>cohere.command-a-03-2025]
    E -->|sem credencial| G[Fallback local<br/>recomendação pré-definida]
    F --> H[Painel dual]
    G --> H
    H --> I[Visão Corporativa B2B<br/>mitigação de ativo]
    H --> J[Visão ESG / Comunidade<br/>protocolo de evacuação]
    I --> K{Human-in-the-Loop<br/>confirmação manual}
    J --> K
```

### Visão Abrigos e Preparação

Terceira opção do menu lateral, organizada em três abas:

- **Mapa de Abrigos**: o usuário escolhe a cidade (ou busca outra, ou usa o GPS) e o mapa mostra abrigos cadastrados no MVP e locais reais buscados no OpenStreetMap, filtráveis por categoria. Ao clicar em um ponto, abre-se a rota no Waze ou no Google Maps. Se a busca no OpenStreetMap falhar, entra uma lista de reserva ilustrativa.
- **Central de Alertas**: cruza eventos ativos da NASA EONET com os abrigos cadastrados (raio de 600 km) e lista os que estão em risco.
- **Checklist de Sobrevivência**: lista de itens de preparação, com indicação do nível de preparo.

Fluxo do mapa de abrigos:

```mermaid
flowchart LR
    U[Usuário<br/>cidade, busca ou GPS] --> M[Mapa interativo<br/>Leaflet]
    O[OpenStreetMap<br/>Overpass e Nominatim] --> M
    N[NASA EONET<br/>alertas próximos] --> M
    M --> R[Rota no Waze<br/>ou Google Maps]
```

## Como rodar localmente

```bash
# 1. Instalar dependências
pip install streamlit requests yfinance pandas oci

# 2. Rodar o painel (a partir da pasta raiz do projeto)
streamlit run frontend/painel_ceo.py
```

Rodando localmente, o app abre em http://localhost:8501. Para usar sem instalar nada, acesse a versão publicada na nuvem: https://aplicativo-geo-capital-engine-3k7pun8ggkjwsyvgb2pgvm.streamlit.app/

### Integração com Oracle (opcional)

O motor de recomendação (`backend/oracle_rag.py`) funciona em dois modos:

- **Real**: requer o SDK `oci` instalado e a variável de ambiente `OCI_COMPARTMENT_ID` configurada, além do arquivo de credenciais `~/.oci/config`.
- **Fallback (padrão)**: se a credencial não estiver configurada, o sistema usa uma recomendação local pré-definida, mantendo o painel estável em demonstrações públicas.

## Capturas de tela (versão publicada no Streamlit Cloud)

**Visão Corporativa (B2B)** — cruza o evento de risco (NASA EONET) com o ativo industrial mais próximo e recomenda ação de mitigação.

![Dashboard Corporativo](screenshots/visao-corporativa.png)

**Visão de Impacto Social / ESG (Comunidade)** — identifica a comunidade vizinha ao evento e recomenda protocolo de evacuação/suporte humanitário.

![Centro de Comando ESG](screenshots/visao-esg.png)

## Documentação completa

Ver `docs/documentacao_oficial_pitch.md` para a documentação oficial do projeto, incluindo a base legal (CONAMA/EIA-RIMA) e o modelo de negócio detalhado.

## Status do projeto (MVP de Hackathon)

- [OK] Cálculo de risco geoespacial funcional
- [OK] Integração real com NASA EONET e Yahoo Finance
- [OK] Visão Abrigos e Preparação: mapa interativo com locais do OpenStreetMap, rotas no Waze/Google Maps, Central de Alertas NASA e checklist
- [OK] Human-in-the-Loop implementado no painel: a ação (simulada) só ocorre após o clique de confirmação do gestor
- [EM ANDAMENTO] Integração com Oracle GenAI: implementada, sujeita a fallback conforme disponibilidade de credencial
- [EM ANDAMENTO] Scripts em `backend/central_executiva.py` e `backend/omni_engine_alertas.py` são provas de conceito isoladas, não conectadas ao painel principal

## Equipe e Contribuições

- **Leonardo Junior Gonzales Mendoza** (RM 373713) — desenvolvimento do painel em Python/Streamlit, integração com as APIs geoespaciais e financeiras, estruturação da arquitetura de IA (Oracle GenAI) e infraestrutura do repositório.
- **Felipe Eunilio Vieira dos Santos** (RM 369771) — concepção do framework de produtização e modelo de negócio (documento "Decision Intelligence"), incluindo o posicionamento B2B e a lógica de Human-in-the-Loop aplicada à solução.
- **Helton Rosa da Silva Abadia** (RM 360372) — ajustes técnicos no código, incluindo correção de um bug no motor de alertas que bloqueava o disparo de múltiplos alertas; alterações já enviadas ao GitHub e em processo de integração à branch principal.

## Limitações conhecidas

- A IA generativa da Oracle roda em modo de fallback na demonstração pública: sem credencial OCI, o sistema usa uma recomendação local pré-definida.
- O disparo real de alertas (SMS/WhatsApp) ainda não está implementado; os botões do painel exibem a confirmação na tela (simulação), sem envio real.
- O nome "RAG" no painel se refere ao motor de recomendação; a etapa de recuperação de dados (ex.: base do EIA/RIMA) é um próximo passo.
- A base de 6 ativos e comunidades do MVP é ilustrativa e fixa no código; o estudo de caso da Bacia de Campos é um cenário de referência.
- Os scripts `backend/central_executiva.py` e `backend/omni_engine_alertas.py` são provas de conceito isoladas, não conectadas ao painel principal.
- Os dados dependem da disponibilidade das APIs públicas (NASA EONET, Yahoo Finance, Overpass e Nominatim).
- No mapa de abrigos, a classificação dos locais do OpenStreetMap é feita pelo nome e pelas tags; locais mal nomeados ou sem tags podem ficar de fora ou aparecer na categoria errada. Os abrigos são cadastrados no MVP, com coordenadas aproximadas.
- A Central de Alertas usa recomendação local pré-definida, sem chamar o Oracle GenAI.
- A validação com usuários ainda é inicial; a validação de campo com comunidades reais é um próximo passo.

## Próximos passos

1. Validação de campo com colônias de pescadores e mentores do setor.
2. Integração ativa com o Oracle GenAI (`cohere.command-a-03-2025`) em produção.
3. Parceria piloto com uma operadora para acessar dados reais de EIA/RIMA.
4. Canal de disparo real (SMS/WhatsApp) para lideranças comunitárias.
