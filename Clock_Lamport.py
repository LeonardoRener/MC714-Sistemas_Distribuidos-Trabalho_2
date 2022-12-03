from mpi4py import MPI
from multiprocessing import Process
import random
import time
import sys

# Classe de Relógio lógico de Lamport:
# Se a acontece antes de b no mesmo processo, então C(a) < C(b).
# Se a e b representam, respectivamente, o envio e o recebimento de uma mensagem, então C(a) < C(b).
# Sejam a e b eventos quaisquer, então C(a) ≠ C(b)
class Lamport:
    def __init__(self, size, rank):
        self.clock = 0
        self.size = size
        self.rank = rank
        log("Create rank {}, clock={}".format(self.rank, self.clock))

    # Envia o valor do clock para o processo destino
    def event(self, dest):
        self.clock += 1
        log("SEND - rank {} sent to rank {}, clock={}".format(self.rank, dest, self.clock))
        MPI.COMM_WORLD.send(self.clock, dest=dest)

    # Recebe o valor do clock, se é maior que o proprio relogio então atualiza, do contrario mantem o relogio.
    def receive(self):
        recv_clock = MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status) + 1

        if (self.clock > recv_clock):
            log("RECEIVE - rank {} received from rank {}, kept the clock={}".format(self.rank, status.Get_source(), self.clock))
        else:
            self.clock = recv_clock
            log("RECEIVE - rank {} received from rank {}, new clock={}".format(self.rank, status.Get_source(), self.clock))

# Funcao para imprimir no console.
def log(string):
    print(string)
    sys.stdout.flush()

# Envia mensagem para todos os outros processos, exeto para ele mesmo.
def send(lamport):
    random.seed(lamport.rank)
    while True:
        dest = random.choice([i for i in range(0,lamport.size) if i not in [lamport.rank]])
        time.sleep(random.randint(1,20))

        lamport.event(dest)

# Recebe mensagens de todos os outros processos.
def recv(lamport):
    log("RANK {} - Aguardando mensagens...".format(lamport.rank))
    while True:
        lamport.receive()

status = MPI.Status()

if __name__ == '__main__':

    comm = MPI.COMM_WORLD
    lamport = Lamport(size=comm.Get_size(), rank=comm.Get_rank())

    # Cria as threads para receber e envia o clock atual
    p1 = Process(target=send, args=(lamport,))
    p2 = Process(target=recv, args=(lamport,))

    # Inicia as threads
    p1.start()
    p2.start()

    # Espera as threads terminarem
    p1.join()
    p2.join()
