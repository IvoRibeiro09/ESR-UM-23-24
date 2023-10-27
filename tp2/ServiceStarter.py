import os
import subprocess


# ciclo que itera sobre os N nodos que temos na rede overlay e abre uma
# bash para cada uma correr a (NodeOverlay.py ficheiroParse)

import os
import subprocess


def main():
    programa = "NodeOverlay.py"
    folder = "/home/ivo/Desktop/ESR/tp2/ESR-UM-23-24/tp2/nodes"
    arquivos = os.listdir(folder)
    print(arquivos)

    for file in arquivos:
        # Verifica se o arquivo é um arquivo regular (não é um diretório)
        if os.path.isfile(os.path.join(folder, file)):
            # Constrói o comando Bash a ser executado
            comando_bash = f"python3 {programa} {os.path.join(folder, file)}"
            print(comando_bash)
            # Verifica se o arquivo do programa existe
            if os.path.exists(programa):
                # Executa o comando Bash
                subprocess.call(comando_bash, shell=True)
            else:
                print(f"O arquivo do programa {programa} não foi encontrado.")
        else:
            print(f"{file} não é um arquivo regular.")


if __name__ == "__main__":
    main()
