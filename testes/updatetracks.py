def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]
def possibelToMerge(caminho1, caminho2):
    pares_str1 = extrair_pares(caminho1)
    pares_str2 = extrair_pares(caminho2)
    for par1 in pares_str1:
        for par2 in pares_str2:
            if par1 == par2:
                return True
    return False     

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
    
def update(lista_de_clientes, lista_de_caminhos):
    caminhos_unificados = []
    for caminho in lista_de_clientes:
        if caminhos_unificados == []:
            caminhos_unificados.append(caminho)
        else:
            for caminho2 in caminhos_unificados:
                if possibelToMerge(caminho, caminho2):
                    caminhos_unificados.remove(caminho2)
                    c = combinar_caminhos(caminho, caminho2)
                    caminhos_unificados.append(c)
                else:
                    caminhos_unificados.append(caminho)

    for c in caminhos_unificados:
        print(c)
        pares = extrair_pares(c)
        inic = pares.pop(0)
        trackToPacket = ""
        for p in pares:
            trackToPacket += f"{p[0].split('.')[-2]}.{p[0].split('.')[-1]}:"
            if "," in p[1]:
                ips = p[1].split(",")
                for i in ips:
                    trackToPacket += f"{i.split('.')[-2]}.{i.split('.')[-1]},"
                trackToPacket = trackToPacket[:-1]
            else:
                trackToPacket += f"{p[1].split('.')[-2]}.{p[1].split('.')[-1]}"
            trackToPacket += "|"
        trackToPacket = trackToPacket[:-1]
        lista_de_caminhos.append((inic[1],trackToPacket))


caminho1 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5"
caminho2 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.7 | 127.0.0.7 -> 127.0.0.6"

lista_de_clientes = []
lista_de_caminhos = []

lista_de_clientes.append(caminho1)

update(lista_de_clientes, lista_de_caminhos)
print(lista_de_caminhos)
lista_de_caminhos.pop()

lista_de_clientes.append(caminho2)

update(lista_de_clientes, lista_de_caminhos)
print(lista_de_caminhos)

def extrair_conexoes(ip, ident, input_string):
    ip_terminação = f"{ip.split('.')[-2]}.{ip.split('.')[-1]}"
    send_list = []
    try:
        if "|" in input_string:
            partes = input_string.split('|')
            for p in partes:
                send_recv = p.split(":")
                if ip_terminação in send_recv[0]:
                    if "," in send_recv[1]:
                        ips = send_recv[1].split(",")
                        for i in ips:
                            send_list.append(f"{ident}{i}")
                    else:
                        send_list.append(f"{ident}{send_recv[1]}")
        else:
            send_recv = input_string.split(":")
            if ip_terminação in send_recv[0]:
                if "," in send_recv[1]:
                    ips = send_recv[1].split(",")
                    for i in ips:
                        send_list.append(f"{ident}{i}")
                else:
                    send_list.append(f"{ident}{send_recv[1]}")
        return send_list
    except Exception as e:
        print("Erro ao criar a lista de tuplos",e)


print(extrair_conexoes("127.0.0.7", "127.0.", lista_de_caminhos[0][1]))