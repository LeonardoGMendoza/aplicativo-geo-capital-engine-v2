const nomes = ["Bar do Bongo", "Padaria Panamá", "Pronto Pizza", "Ótica Grupa", "UBS Vila Ramos", "UPA São Sebastião", "Hospital Bruno Born", "ONG Mãos Dadas", "Pronto Socorro Central"];

nomes.forEach(nome => {
    let op = '';
    let cat = 'Descartado';
    if (/\bUPA\b/.test(nome) || /\bUPA\b/.test(op)) cat = 'u';
    else if (/\b(UBS|UBSF|USF|AMA)\b/.test(nome) || nome.match(/Unidade de Sa/i) || /\b(UBS|SUS)\b/.test(op)) cat = 'u';
    else if (/\bONG\b/.test(nome) || nome.match(/abrigo|refugio|refúgio|assistência/i)) cat = 'o';
    else if (nome.match(/Pronto[- ]?(Socorro|Atendimento)|Sa[úu]de|Cl[íi]nica/i)) cat = 'u';
    else if (nome.match(/hospital/i)) cat = 'h';
    
    console.log(nome + " -> " + cat);
});
