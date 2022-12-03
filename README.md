# MC714-Sistemas_Distribuidos-Trabalho_2
Este trabalho foca na implementação de algoritmos distribuídos.

# Instrucoes para execucao:
Realize a instalacao da biblioteca mpi4py utilizando o comando ~pip install mpi4py~.
Execute o codigo atravez do comando "mpiexec -np PROCESSOS python ARQUIVO.py" onde PROCESSOS representa o numero de processos criados (deve ser substituido por um valor inteiro), e ARQUIVO o nome do arquivo do algoritimo desejado ("Clock_Lamport", "Mutual_Exclusion" ou "Leader_Election").

## Relógio lógico de Lamport.
O arquivo Clock_Lamport.py implementa um relógio lógico de lamport, que é um algoritmo de relógio lógico simples usado para determinar a ordem dos eventos em um sistema de computador distribuído.

Fontes utilizadas: https://en.wikipedia.org/wiki/Lamport_timestamp e https://www.geeksforgeeks.org/lamports-logical-clock/

## Algoritmo de exclusão mútua.
O arquivo Mutual_Exclusion.py implementa um algoritmo de exclusão mútua, utilizando a estrategia de algoritmo centralizado, simulando como exclusão mútua é feita em monoprocessador.
Para isso, um processo é eleito coordenador e os outros processos que querem acessar o recurso compartilhado devem seguer os passos:
- Envia mensagem ao coordenador declarando qual recurso quer acessar e solicitando permissão.
- Se recurso está livre, coordenador responde com permissão.
- Se não está livre, pode negar permissão ou não responder até estar livre.

Fontes utilizadas: Slide da aula de Sistemas Distribuidos (MC714), 2° semestre de 2022, Disponivel em: https://drive.google.com/file/d/1LWHh63-qsv0KD2agniVxqhRRqg7b03zo/view

## Algoritmo de eleição de líder.
O arquivo Leader_Election.py implementa um algoritmo de eleição de líder, utilizando a estrategia do algoritmo do valentão: Nesse algoritmo, quando um processo P qualquer nota que coordenador não está mais respondendo, inicia um processo de eleição, seguindo as seguintes regras:
- Processos podem receber mensagem ELEIÇÃO a qualquer momento de nós com número mais baixo.
- Receptor envia OK de volta ao remetente, indicando que está vivo e que tomará o poder.
- Receptor convoca uma eleição (a não ser que já tenha convocado uma)
- Converge para situação onde todos desistem, exceto um, que será o novo coordenador.

Fontes utilizadas: Slide da aula de Sistemas Distribuidos (MC714), 2° semestre de 2022, Disponivel em: https://drive.google.com/file/d/1vBKJWkWHk66i8q93xQciEFcpdc_BwpeP/view