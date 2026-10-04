# Documentação do Projeto: Omni-EcoRescue

## 1. Visão Geral
O **Omni-EcoRescue** é um sistema preditivo voltado para a prevenção de perdas industriais em desastres ambientais e mitigação de impactos sociais em zonas de vulnerabilidade. O software opera em um painel dual, unindo o interesse financeiro-corporativo (B2B) às obrigações de responsabilidade social (ESG).

## 2. O Problema
Desastres climáticos severos atingem infraestruturas industriais críticas (offshore, mineração, agronegócio). 
A falta de precisão e a tomada de decisão logística "no escuro" geram duas consequências catastróficas:
1. **Dano Corporativo:** Perda estrutural bilionária e desvalorização imediata de ativos na bolsa.
2. **Dano Social:** Comunidades no entorno e associações locais são afetadas por riscos secundários (vazamentos tóxicos, contaminação hídrica) sem tempo hábil para evacuação.

## 3. A Solução
O painel cruza, em tempo real, monitoramento geoespacial com dados financeiros, passando por um motor de Inteligência Artificial para gerar planos de ação específicos.

- **Visão Corporativa (B2B):** Foco em mitigação de danos estruturais. Ao detectar uma ameaça (ex: furacão no Golfo do México), o sistema avalia o valor de mercado do ativo em risco e apresenta ao gestor humano uma recomendação de ação. A decisão final e o acionamento, via botão de confirmação no painel, permanecem sob controle humano — Human-in-the-Loop.
- **Visão de Impacto Social (ESG/Comunidade):** Foco em resgate humanitário. O alerta corporativo ativa simultaneamente um protocolo direcionado às comunidades vizinhas mapeadas pelo estudo de impacto ambiental da empresa, indicando evacuação, envio de kits de descontaminação e prioridade para grupos vulneráveis.

## 4. Estudo de Caso (Foco do Pitch)
* **Local:** Bacia de Campos (Litoral do Rio de Janeiro).
* **Risco Corporativo:** Infraestrutura da Petrobras ameaçada por tempestades severas (Ciclones Extratropicais).
* **Impacto Social (A Comunidade):** Colônia de Pescadores Z3 de Macaé.
* **O Fluxo:** Ao prever a tempestade sobre o ativo, o alerta é gerado. Mediante validação humana, a operação pode ser interrompida para salvar a estrutura, e um aviso prévio fica pronto para ser disparado, via confirmação no painel, para a associação de pescadores proteger suas embarcações e famílias antes da chegada de qualquer resíduo.

## 5. Viabilidade e Base Legal
O impacto social do projeto (notificação da comunidade) não exige que o governo pague pela tecnologia, pois se sustenta no modelo ESG corporativo. 
O mapeamento das lideranças (o "telefone" da comunidade) é baseado na **Resolução CONAMA 01/1986 (EIA/RIMA)**, que obriga empresas a realizarem diagnósticos socioeconômicos da região. Ademais, o vínculo com a Colônia Z3 já existe formalmente via **Plano de Compensação Ambiental**. O Omni-EcoRescue propõe automatizar o uso prático desses dados, hoje estáticos.

## 6. Arquitetura Técnica
A arquitetura MVP é sustentada por:
* **Frontend/Interface:** Construída em `Streamlit` (`painel_ceo.py`), operando com menu de controle dual (B2B vs ESG).
* **Processamento de Dados:** Bibliotecas `pandas` e `math` (Haversine para cálculo de risco espacial com limite de 600km).
* **Integrações Externas (APIs):**
  * **Clima:** NASA EONET (Rastreamento ao vivo de tempestades, vulcões, incêndios).
  * **Mercado:** Yahoo Finance (Cotação em tempo real dos ativos afetados).
* **Inteligência Artificial:** `Oracle OCI Generative AI`.
  * *Implementação Segura:* Estruturada via SDK oficial (`oci`) consumindo o modelo `cohere.command-a-03-2025`, com tratamento de erro (fallback local) para garantir a estabilidade do painel caso a chave de API não esteja configurada ou haja falha de conexão durante a apresentação.
