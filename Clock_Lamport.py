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
        log("SEND - Rank {} enviou para o rank {}, clock={}".format(self.rank, dest, self.clock))
        MPI.COMM_WORLD.send(self.clock, dest=dest)

    def receive(self, dest, tag):
        return MPI.COMM_WORLD.recv(source=dest, tag=tag, status=status)

# Funcao para imprimir no console.
def log(string):
    print(string)
    sys.stdout.flush()

# Envia mensagem para todos os outros processos, exeto para ele mesmo.
def send(lamport):
    
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
    process = Lamport(size=comm.Get_size(), rank=comm.Get_rank())

    random.seed(process.rank)
    timeToSend = random.randint(5,20)
    initialTime = time.time()

    while True:
        # De tempos em tempos envia um evento para um processo aleatorio.
        if (time.time() - initialTime) > timeToSend:
            dest = random.choice([i for i in range(0,process.size) if i not in [process.rank]])
            timeToSend = random.randint(5,20)
            initialTime = time.time()
            process.event(dest)
        
        # Se não recebeu nenhuma mensagem, continua a execusao:
        if not comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
            time.sleep(1)

        # Se recebeu uma mensagem, verifica se precisa atualizar seu clock:
        else:
            recv_clock = process.receive(MPI.ANY_SOURCE, MPI.ANY_TAG) + 1

            # Se o clock atual eh maior que o recebido:
            if (process.clock > recv_clock):
                log("\nRECEIVE - Rank {} recebeu uma mensagem de {}, manteu seu clock como {}\n".format(process.rank, status.Get_source(), process.clock))
            
            # Do contrario:
            else:
                process.clock = recv_clock
                log("\nRECEIVE - Rank {} recebeu uma mensagem de {}, atualizou o clock para {}\n".format(process.rank, status.Get_source(), process.clock))
