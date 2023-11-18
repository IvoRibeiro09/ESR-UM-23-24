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
            partes = input_string.split(' | ',1)
            conexao = partes[0].split(" -> ")
            if "," in conexao[1]:
                ips = conexao[1].split(",")
                for i in ips:
                    if i in partes[1]:
                        lista.append((i, partes[1]))
            else:
                if conexao[1] in  partes[1]:
                    lista.append((conexao[1], partes[1]))
        else:
            conexao = input_string.split(" -> ")
            if "," in conexao[1]:
                ips = conexao[1].split(",")
                for i in ips:
                    lista.append((i,""))
            else:
                lista.append((conexao[1],""))
    except Exception as e:
        print("Erro ao criar a lista de tuplos",e)
    
def possibelToMerge(caminho, caminho2):
    pares_str1 = extrair_pares(caminho)
    pares_str2 = extrair_pares(caminho2)
    for par1 in pares_str1:
        for par2 in pares_str2:
            if par1 == par2:
                return True
    return False  

def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]

def combinar_caminhos(caminho1, caminho2):
    pares_str1 = extrair_pares(caminho1)
    pares_str2 = extrair_pares(caminho2)
    conexoes_dict = {}
    for par in pares_str1:
        if par[0] not in conexoes_dict:
            conexoes_dict[par[0]] = par[1]
        if par[1] not in conexoes_dict[par[0]]:
            aux = conexoes_dict[par[0]]
            conexoes_dict[par[0]] = aux + "," + par[1] 

    for par in pares_str2:
        if par[0] not in conexoes_dict:
            conexoes_dict[par[0]] = par[1]
        if par[1] not in conexoes_dict[par[0]]:
            aux = conexoes_dict[par[0]]
            conexoes_dict[par[0]] = aux + "," + par[1] 

    partes = []
    for inicio, fins in conexoes_dict.items():
        partes.append(f"{inicio} -> {fins}")
    return ' | '.join(partes)