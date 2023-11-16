
def extrair_conexoes(input_string):
    #lista de tuplos (endereço para enviar, caminho a partir daí)
    lista = []
    if "|" in input_string:
        parts = input_string.split(' | ')
        primeiro_conjunto = parts[0]
        fst = primeiro_conjunto.split(" -> ")
        ips = [fst[1]]
        novas_parts = []

        for p in parts[1:]:
            if fst[0] in p:
                ips.append(p.split(" -> ")[1])
            else:
                novas_parts.append(p)

        resto = ' | '.join(novas_parts)
        for i in ips:
            if i in resto:
                lista.append((i, resto))
            else: 
                lista.append((i, ""))
        return lista
    else:
        fst = input_string.split(" -> ")
        lista.append(fst[1], "")
        return lista
    
def possibelToMerge(caminho, Node_Track):
    pares_str1 = extrair_pares(caminho)
    for i in Node_Track:
        pares_str2 = extrair_pares(i[1])
        for par1 in pares_str1:
            for par2 in pares_str2:
                if par1 == par2:
                    return i[1]
    return None  
    
def mergeCaminhos(caminho, Node_Track):
    pares_str1 = extrair_pares(caminho)
    pares_str2 = extrair_pares(Node_Track)
    novos_pares = [par2 for par2 in pares_str2 if par2 not in pares_str1]
    pares_combinados = pares_str1 + novos_pares
    return ' | '.join([f"{par[0]} -> {par[1]}" for par in pares_combinados])

def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]
        
# Exemplo de uso
e0 = [('127.0.0.3', '127.0.0.3 -> 127.0.0.4 | 127.0.0.3 -> 127.0.0.7 | 127.0.0.4 -> 127.0.0.5'),
      ('127.0.0.5', '127.0.0.4 -> 127.0.0.7'),
      ('127.0.0.6', '')]
e2 = '127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.6'

selected = possibelToMerge(e2, e0)
print(selected)

merge = mergeCaminhos(extrair_conexoes(e2)[0][1], selected)
print(merge)

print("ola")
tes = "127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.6 | 127.0.0.3 -> 127.0.0.7 | 127.0.0.4 -> 127.0.0.5"
i=0
while i < 2:
    result = extrair_conexoes(tes)
    print(result)
    tes = result[0][1]
    i+=1