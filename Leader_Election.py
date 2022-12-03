from mpi4py import MPI
import random
import time
import sys

status = MPI.Status()
TIMEOUT_LEADER_TEST = 15
TIMEOUT = 10

# Tipos de mensagens.
class MessageType():
    OK = 0
    ELECTION = 1
    TAKE_POWER = 2

# Classe que representa os processos existentes.
class ProcessClass():
    def __init__(self, size, rank, leader):
        self.leader = leader
        self.size = size
        self.rank = rank
        log("Create rank {}".format(self.rank))

    def receive(self, dest, tag):
        return MPI.COMM_WORLD.recv(source=dest, tag=tag, status=status)

    def sendAll(self, message, tag):
        for i in range(self.size):
            if i != self.rank:
                self.send(message, tag, i)

    def sendToHighers(self, message, tag):
        for i in range(self.size-1, self.rank, -1):
            self.send(message, tag, i)

    def send(self, message, tag, dest):
        MPI.COMM_WORLD.send(message, tag=tag, dest=dest)

# Funcao para imprimir no console.
def log(string):
    print(string)
    sys.stdout.flush()
    
if __name__ == '__main__':
    comm = MPI.COMM_WORLD

    # Recebe o lider inicial, atravez do argumento da linha de comando.
    try:
        initialLeader = int(argvImagemEntrada = sys.argv[1])
    except:
        initialLeader = comm.Get_size()-1
    
    process = ProcessClass(size=comm.Get_size(), rank=comm.Get_rank(), leader=initialLeader)

    waitingForLeader = False
    waitingForElection = False
    initialWaitingTime = time.time()
    lastTimeLeader = time.time()

    while True:
        # Apos 15 segundos como lider o processo fica desativado, para testar o sistema de eleicao.
        if process.rank == process.leader and (time.time() - lastTimeLeader) > TIMEOUT_LEADER_TEST:
            log("\nRANK {} - Finalizando processo!!!\n".format(process.rank))
            exit(0)

        # Aleatoriamente checa se o lider está respondendo:
        if process.rank != process.leader and not waitingForLeader and not waitingForElection and random.choice([True, False, False]):
            log("RANK {} - Checando o lider {} ".format(process.rank, process.leader))
            process.send("Checando o lider", MessageType.OK, process.leader)
            initialWaitingTime = time.time()
            waitingForLeader = True

        # Se não recebeu nenhuma mensagem:
        if not comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
            # Se o lider não respondeu, começa uma eleição:
            if waitingForLeader and  (time.time() - initialWaitingTime) > TIMEOUT:
                log("RANK {} - Propondo eleicao!".format(process.rank))
                process.sendToHighers(MessageType.ELECTION, MessageType.ELECTION)
                waitingForLeader = False
                waitingForElection = True
                initialWaitingTime = time.time()

            # Se iniciou uma eleição e não recebeu resposta dos processos de maior identificador, se torna lider:
            elif waitingForElection and (time.time() - initialWaitingTime) > TIMEOUT:
                log("\nRANK {} - Se tornando lider!\n".format(process.rank))
                process.sendAll(MessageType.TAKE_POWER, MessageType.TAKE_POWER)
                process.leader = process.rank
                lastTimeLeader = time.time()
                waitingForLeader = waitingForElection = False

            # Do contrario continua suas atividades.
            else:
                time.sleep(1)

        # Se recebeu uma mensagem:
        else:
            message = process.receive(MPI.ANY_SOURCE, MPI.ANY_TAG)
            source = status.Get_source()
            tag = status.Get_tag()

            # Se é o lider, e não é uma mensagem de mudança de lider, responde que está ativo:
            if tag != MessageType.TAKE_POWER and process.rank == process.leader:
                process.send("Estou ativo.", MessageType.OK, source)

            # Se é do tipo eleição, responde que está ativo e inicia o processo para tomar o poder:
            elif tag == MessageType.ELECTION:
                log("RANK {} - Recebida proposta de eleicao, respondendo que esta ativo.".format(process.rank))
                waitingForLeader = False
                process.send("Estou ativo.", MessageType.OK, source)

                if not waitingForElection:
                    log("RANK {} - Checando processos superiores!".format(process.rank))
                    waitingForElection = True
                    process.sendToHighers(MessageType.ELECTION, MessageType.ELECTION)

            # Se é do tipo take power, define o novo lider:
            elif tag == MessageType.TAKE_POWER:
                log("RANK {} - O processo {} se tornou o novo lider".format(process.rank, source))
                lastTimeLeader = time.time()
                process.leader = source
                waitingForLeader = waitingForElection = False

            # Se o lider enviou uma mensagem do tipo ok, e estava esperando essa mensagem:
            elif tag == MessageType.OK and source == process.leader and waitingForLeader:
                log("RANK {} - Verificado que o lider esta ativo.".format(process.rank))
                waitingForLeader = False

            # Se um processo de rank superior enviou uma mensagem do tipo leader ok, e estava esperando essa mensagem:
            elif tag == MessageType.OK and source > process.rank and waitingForElection:
                log("RANK {} - Verificado que o processo de rank superior {} esta ativo.".format(process.rank, source))
                waitingForElection = False
