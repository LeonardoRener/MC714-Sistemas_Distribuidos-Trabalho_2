from mpi4py import MPI
import random
from queue import Queue
import time
import sys

# Tipos de requisições.
class MessageType():
    MUTEX_REQUEST = 0
    MUTEX_CONCESSION = 1
    MUTEX_FREE = 2

# Classe que representa o recurso compatilhado entro os processos.
class SharedResource():
    def __init__(self):
        self.value = 0

    def getValue(self):
        return self.value

    def setValue(self, newValue):
        log("\nShared resource changed from {} to {}\n".format(self.value, newValue))
        self.value = newValue

# Classe que representa os processos existentes, o processo 0 é eleito coordenador.
class ProcessClass():
    def __init__(self, size, rank):
        self.clock = 0
        self.size = size
        self.rank = rank
        self.isCoordinator = rank == 0
        log("Create rank {}, clock={}".format(self.rank, self.clock))

# Função que realiza modificações no recurso compartilhando de tempos em tempos.
def sendRequests(process):
    random.seed(process.rank)
    while True:
        time.sleep(random.randint(1,20))
        log("RANK {} - Requesting access to the resource".format(process.rank))

        # Envia a solicitação de uso.
        MPI.COMM_WORLD.send(None, dest=0, tag=MessageType.MUTEX_REQUEST)

        # Aguarda a liberação do recurso.
        resource = MPI.COMM_WORLD.recv(source=0, tag=MessageType.MUTEX_CONCESSION, status=status)

        # Utiliza a região critica.
        resource.setValue(process.rank)

        # Compartilha que terminou de utilizar o recurso.
        MPI.COMM_WORLD.send(resource, dest=0, tag=MessageType.MUTEX_FREE)

# Controle do recurso compartilhado.
def coodinatorControll():
    sharedResource = SharedResource()
    queue = Queue()
    busy = False

    while True:
        message = MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        
        # Trata pedidos de requisição de uso.
        if status.Get_tag() ==  MessageType.MUTEX_REQUEST:
            if not busy:
                busy = True
                log("COODINATOR - Sharing the resource with {}.".format(status.Get_source()))
                MPI.COMM_WORLD.send(sharedResource, status.Get_source(), tag=MessageType.MUTEX_CONCESSION)
            else:
                log("COODINATOR - {} queued to access the resource.".format(status.Get_source()))
                queue.put(status.Get_source())

        # Trata a liberação do uso do recurso.
        elif status.Get_tag() == MessageType.MUTEX_FREE:
            log("COODINATOR - {} has finished using the resource.".format(status.Get_source()))
            sharedResource = message

            if queue.empty():
                busy = False
            else:
                dest = queue.get()
                log("COODINATOR - Sharing the resource with {}.".format(dest))
                MPI.COMM_WORLD.send(sharedResource, dest=dest, tag=MessageType.MUTEX_CONCESSION)

# Funcao para imprimir no console.
def log(string):
    print(string)
    sys.stdout.flush()

status = MPI.Status()

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    process = ProcessClass(size=comm.Get_size(), rank=comm.Get_rank())

    if process.isCoordinator:
        coodinatorControll()
    else:
        sendRequests(process)
