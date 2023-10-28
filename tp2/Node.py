import sys
import socket
from NodeData import *
import threading

def lissenServer():
    while True:
        return

def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    #thread = threading.Thread(target=, args=)
    print("aqui")
    


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função NodeOverlay.py!!")