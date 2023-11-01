import sys
from tkinter import Tk
from ServerGUI import *

if __name__ == "__main__":
	try:
		RP_IP = '127.0.0.1'
		porta = 12345
	except:
		print("[Usage: Cliente.py]\n")	
	
    # Criar um servidor
	janela = Tk()
	server = ServerGUI(janela, RP_IP, porta)
	server.janela.title("Servidor")
	janela.mainloop()