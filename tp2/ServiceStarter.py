import os




# ciclo que itera sobre os N nodos que temos na rede overlay e abre uma
# bash para cada uma correr a (NodeOverlay.py ficheiroParse)

def main():
    programa = "NodeOverlay.py"
    folder = "/home/ivo/Desktop/ESR/ESR-UM-23-24/tp2/nodes"
    arquivos = os.listdir(folder)
    print(arquivos)

    for file in arquivos:
        # Verifica se o arquivo é um arquivo regular (não é um diretório)
        if os.path.isfile(os.path.join(folder, file)):
            # Constrói o comando Bash a ser executado
            comando_bash = f"python3 {programa} {os.path.join(folder, file)}"
            print(comando_bash)

            # abrir um novo terminal e executa o comando
            os.system(f"gnome-terminal -- /bin/bash -c '{comando_bash}; read -p \"Press Enter to exit\"'")

        else:
            print(f"{file} não é um arquivo regular.")


if __name__ == "__main__":
    main()
