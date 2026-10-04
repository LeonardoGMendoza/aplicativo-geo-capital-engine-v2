import re
with open('frontend/painel_ceo.py', 'r', encoding='utf-8') as f:
    text = f.read()

st = text.find('st.caption(')
en = text.find(')', st) + 1

new_cap = 'st.caption(\n            "\u2139\ufe0f **Nota:** os locais (hospitais, UBS/UPA, farm\xe1cias, mercados, hot\xe9is etc.) s\xe3o buscados no OpenStreetMap; se a busca falhar, entra uma lista de reserva ilustrativa. Os abrigos s\xe3o cadastrados no MVP, com coordenadas aproximadas. Ao clicar em um ponto, a rota abre no Waze ou no Google Maps, a partir do ponto azul."\n        )'

text = text[:st] + new_cap + text[en:]

with open('frontend/painel_ceo.py', 'w', encoding='utf-8', newline='') as f:
    f.write(text)

with open('frontend/mapa_interativo.py', 'r', encoding='utf-8') as f:
    cm = f.read()

cm = cm.replace(
    'var wz = "https://waze.com/ul?ll="+p.lat+","+p.lon+"&navigate=yes";',
    'var wz = "https://www.waze.com/live-map/directions?navigate=yes&to=ll."+p.lat+"%2C"+p.lon+"&from=ll."+uLat+"%2C"+uLng;"'
).replace(
    'var gm = "https://www.google.com/maps/dir/?api=1&destination="+p.lat+","+p.lon;',
    'var gm = "https://www.google.com/maps/dir/?api=1&origin="+uLat+","+uLng+"&destination="+p.lat+","+p.lon;'
)

cm = re.sub(
    r"(if\(el\.tags\['addr:street'\]\) end=el\.tags\['addr:street'\]\+\(el\.tags\['addr:housenumber'\]\?', '\+el\.tags\['addr:housenumber'\]:''\))\+'[^']*SP';",
    r"\1;", 
    cm
)

cm = cm.replace('    else listas.h.push(p);\n', '', 1)

cm = cm.replace(
    'nome.match(/UPA/i)||op.match(/UPA/i)',
    r'/\\bUPA\\b/.test(nome)||/\\bUPA\\b/.test(op)'
)

cm = cm.replace(
    r'nome.match(/UBS|UBSF|USF|AMA\b|Unidade de Sa/i)||op.match(/UBS|SUS/i)',
    r'/\\b(UBS|UBSF|USF|AMA)\\b/.test(nome)||nome.match(/Unidade de Sa/i)||/\\b(UBS|SUS)\\b/.test(op)'
)

cm = cm.replace(
    'nome.match(/ONG|abrigo|refugio|ref\u00fagio|assist\u00eancia/i)',
    r'/\\bONG\\b/.test(nome)||nome.match(/abrigo|refugio|ref\u00fagio|assist\u00eancia/i)'
)

cm = cm.replace(
    'nome.match(/Pronto|Sa\u00fade|Saude|clinica|cl\u00ednica/i)',
    r'nome.match(/Pronto[- ]?(Socorro|Atendimento)|Sa[\u00fau]de|Cl[\u00edi]nica/i)'
)

with open('frontend/mapa_interativo.py', 'w', encoding='utf-8', newline='') as f:
    f.write(cm)

print("PATCHED ALL")
