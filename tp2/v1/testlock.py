import threading
import queue

def thread1(q, event):
    while True:
        message = input("Thread 1: Digite uma mensagem (ou 'q' para sair): ")
        if message == 'q':
            break
        q.clear()
        q.put(message)  # Coloca a mensagem na fila
        event.set()     # Sinaliza que há uma mensagem na fila

def thread2(q, event):
    while True:
        event.wait()  # Espera até receber um sinal
        message = q.get()  # Obtém a mensagem da fila
        event.clear()  # Limpa o sinal
        print("Thread 2: Mensagem recebida:", message)

if __name__ == "__main__":
    message_queue = queue.Queue()
    event = threading.Event()

    t1 = threading.Thread(target=thread1, args=(message_queue, event))
    t2 = threading.Thread(target=thread2, args=(message_queue, event))

    t1.start()
    t2.start()

    t1.join()
    t2.join()