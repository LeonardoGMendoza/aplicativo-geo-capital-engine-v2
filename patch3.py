import re
with open('frontend/mapa_interativo.py', 'r', encoding='utf-8') as f:
    cm = f.read()

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

print("PATCH 3 OK")
