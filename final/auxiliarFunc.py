import os, re

'''
Metodos auxiliares que são usados pelas diferentes estruturas
'''

# Metodo que retorna o nome do video quando lhe é passado o caminho para o mesmo
def getVideoName(video):
    nomeExtensao = os.path.basename(video)
    video_sem_extensao, _ = os.path.splitext(nomeExtensao)
    return video_sem_extensao

# Metodo que retorna um inteiro seguido de um " - "
def extrair_numero(texto):
    padrao = r'[a-z]*-\s*(\d+)'
    correspondencia = re.search(padrao, texto)
    numero_porta = correspondencia.group(1)
    return int(numero_porta)

# Metodo que retorna a string seguida de um " - "
def extrair_texto(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)'
    correspondencia = re.search(padrao, texto)
    return correspondencia.group(1)

# Metodo que retorna um tuplo com uma string e um inteiro seguida de um " - " e separados por um " - "
def extrair_texto_numero(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)\s+-\s+(\d+)'
    correspondencia = re.search(padrao, texto)
    return (correspondencia.group(1), int(correspondencia.group(2)))

# Metodo inverte uma conexão para ser usada na ordem certa pelo RP
def inverter_relacoes(mensagens):
    if "|" in mensagens:
        relacoes = mensagens.split(' | ')
        mensagens_invertidas = ""
        while relacoes:
            conn = relacoes.pop()
            conn = invert_ip_addresses(conn)
            mensagens_invertidas += conn + " | "
            
        mensagens_invertidas = mensagens_invertidas[:-3] 
    else:
        mensagens_invertidas = invert_ip_addresses(mensagens)
    return mensagens_invertidas

def invert_ip_addresses(address_string):
    addresses = address_string.split('<-')
    inverted_address = f"{addresses[1].strip()} -> {addresses[0].strip()}"
    return inverted_address

# Metodo que permite criar e adicionar caminhos a enviar por uma stream
def extrair_conexoes(lista, input_string):
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
    
# Metodo que verifica se dois caminhos podem ser unficados 
def possibelToMerge(caminho, caminho2):
    pares_str1 = extrair_pares(caminho)
    pares_str2 = extrair_pares(caminho2)
    for par1 in pares_str1:
        for par2 in pares_str2:
            if par1 == par2:
                return True
    return False  

# Metodo auxiliar que separa as conexões em pares
def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]

# Metodo que combina os dois caminhos que podem ser unificados num só caminho
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

# Metodo que elimina o caminho para um cliente do caminho definido na stream
def splitTracks(track, client_ip):
    partes = track.split(" | ")
    last = partes.pop()
    if "," in last:
        conn = last.split(" -> ")
        ips = conn[1].split(",")
        novos_ips = f"{conn[0]} -> "
        novos_ips += ",".join(ip for ip in ips if ip != client_ip)

        partes.append(novos_ips)
        return ' | '.join(partes)
    return None