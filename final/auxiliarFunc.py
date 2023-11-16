import os, re

def getVideoName(video):
    # nome do ficheiro sem o caminho
    nomeExtensao = os.path.basename(video)
    video_sem_extensao, extensao = os.path.splitext(nomeExtensao)
    return video_sem_extensao

def extrair_numero(texto):
    padrao = r'[a-z]*-\s*(\d+)'
    correspondencia = re.search(padrao, texto)
    numero_porta = correspondencia.group(1)
    return int(numero_porta)

def extrair_texto(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)'
    correspondencia = re.search(padrao, texto)
    return correspondencia.group(1)

def extrair_texto_numero(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)\s+-\s+(\d+)'
    correspondencia = re.search(padrao, texto)
    return (correspondencia.group(1), int(correspondencia.group(2)))

def inverter_relacoes(mensagens):
    # Dividir as mensagens em uma lista usando o caractere '|' como delimitador
    if "|" in mensagens:
        relacoes = mensagens.split(' | ')
        mensagens_invertidas = ""
        while relacoes:
            conn = relacoes.pop()
            conn = invert_ip_addresses(conn)
            mensagens_invertidas += conn + " | "
            
        # Inverter a ordem das relações
        mensagens_invertidas = mensagens_invertidas[:-3] 
    else:
        # Inverter a ordem das relações
        mensagens_invertidas = invert_ip_addresses(mensagens)

    return mensagens_invertidas

def invert_ip_addresses(address_string):
    # Separa os dois endereços usando '<-' como delimitador
    addresses = address_string.split('<-')

    # Inverte a ordem dos endereços e os une com '->' como separador
    inverted_address = f"{addresses[1].strip()} -> {addresses[0].strip()}"

    return inverted_address

def extrair_conexoes(lista, input_string):
    #lista de tuplos (endereço para enviar, caminho a partir daí)
    try:
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
        else:
            fst = input_string.split(" -> ")
            lista.append((fst[1], ""))
    except Exception as e:
        print("Erro ao criar a lista de tuplos",e)
    
def possibelToMerge(caminho, Node_Track):
    pares_str1 = extrair_pares(caminho)
    for i in Node_Track:
        pares_str2 = extrair_pares(i[1])
        for par1 in pares_str1:
            for par2 in pares_str2:
                if par1 == par2:
                    Node_Track.remove(i)
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