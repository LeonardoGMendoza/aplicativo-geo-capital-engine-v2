import re
with open('frontend/painel_ceo.py', 'r', encoding='utf-8') as f:
    text = f.read()

st = text.find('st.caption(')
en = text.find(')', st) + 1

new_cap = 'st.caption(\n            "\u2139\ufe0f **Nota:** os locais (hospitais, UBS/UPA, farm\xe1cias, mercados, hot\xe9is etc.) s\xe3o buscados no OpenStreetMap; se a busca falhar, entra uma lista de reserva ilustrativa. Os abrigos s\xe3o cadastrados no MVP, com coordenadas aproximadas. Ao clicar em um ponto, a rota abre no Waze ou no Google Maps, a partir do ponto azul."\n        )'

text = text[:st] + new_cap + text[en:]

with open('frontend/painel_ceo.py', 'w', encoding='utf-8', newline='') as f:
    f.write(text)
print("CEO PATCHED")
