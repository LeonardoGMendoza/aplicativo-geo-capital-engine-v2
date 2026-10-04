import sys, re

with open('frontend/mapa_interativo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# MUDANCA 1
wz_old = 'var wz = "https://waze.com/ul?ll="+p.lat+","+p.lon+"&navigate=yes";'
wz_new = 'var wz = "https://www.waze.com/live-map/directions?navigate=yes&to=ll."+p.lat+"%2C"+p.lon+"&from=ll."+uLat+"%2C"+uLng;'
gm_old = 'var gm = "https://www.google.com/maps/dir/?api=1&destination="+p.lat+","+p.lon;'
gm_new = 'var gm = "https://www.google.com/maps/dir/?api=1&origin="+uLat+","+uLng+"&destination="+p.lat+","+p.lon;'

c = content.replace(wz_old, wz_new)
c = c.replace(gm_old, gm_new)

if c == content:
    print('FALHA MUDANCA 1')
    sys.exit(1)

# MUDANCA 2: Remova o trecho +' - SP' do endereco em processarOverpass
# O texto exato no arquivo pode ter problemas de encoding no dash, vamos usar regex
# Antes: if(el.tags['addr:street']) end=el.tags['addr:street']+(el.tags['addr:housenumber']?', '+el.tags['addr:housenumber']:'')+' - SP';
c2 = re.sub(
    r"(if\(el\.tags\['addr:street'\]\) end=el\.tags\['addr:street'\]\+\(el\.tags\['addr:housenumber'\]\?', '\+el\.tags\['addr:housenumber'\]:''\))\+'[^']*SP';",
    r"\1;", 
    c
)

if c2 == c:
    print('FALHA MUDANCA 2')
    sys.exit(1)
c = c2

# MUDANCA 3: O ultimo "else listas.h.push(p);" deve ser REMOVIDO em processarOverpass
# A linha e: else listas.h.push(p);
# Vamos achar no processarOverpass
idx = c.find('else listas.h.push(p);')
if idx == -1:
    print('FALHA MUDANCA 3 - nao achou 1')
    sys.exit(1)
# we need to make sure we don't remove the one in carregarFallback, which is further down
# so we replace ONLY the first occurrence (since processarOverpass is before carregarFallback)
c3 = c.replace('else listas.h.push(p);', '', 1)
if c3 == c:
    print('FALHA MUDANCA 3')
    sys.exit(1)
c = c3

# MUDANCA 4: regexes
# A: nome.match(/UPA/i)||op.match(/UPA/i) -> /\\\\bUPA\\\\b/.test(nome)||/\\\\bUPA\\\\b/.test(op)
c = c.replace(
    'nome.match(/UPA/i)||op.match(/UPA/i)',
    '/\\\\bUPA\\\\b/.test(nome)||/\\\\bUPA\\\\b/.test(op)'
)

# B: nome.match(/UBS|UBSF|USF|AMA\\b|Unidade de Sa/i)||op.match(/UBS|SUS/i) 
# Wait, in the file, does it have \\b or \b? In the python script I'm writing, let's use exact match
# We should probably use regex replace again or exact string
c = c.replace(
    r'nome.match(/UBS|UBSF|USF|AMA\b|Unidade de Sa/i)||op.match(/UBS|SUS/i)',
    r'/\\b(UBS|UBSF|USF|AMA)\\b/.test(nome)||nome.match(/Unidade de Sa/i)||/\\b(UBS|SUS)\\b/.test(op)'
)

# C: nome.match(/ONG|abrigo|refugio|refúgio|assistência/i)
c = c.replace(
    'nome.match(/ONG|abrigo|refugio|refúgio|assistência/i)',
    '/\\\\bONG\\\\b/.test(nome)||nome.match(/abrigo|refugio|refúgio|assistência/i)'
)

# D: nome.match(/Pronto|Saúde|Saude|clinica|clínica/i)
c = c.replace(
    'nome.match(/Pronto|Saúde|Saude|clinica|clínica/i)',
    'nome.match(/Pronto[- ]?(Socorro|Atendimento)|Sa[úu]de|Cl[íi]nica/i)'
)

with open('frontend/mapa_interativo.py', 'w', encoding='utf-8', newline='') as f:
    f.write(c)

print('frontend/mapa_interativo.py PATCHED')
