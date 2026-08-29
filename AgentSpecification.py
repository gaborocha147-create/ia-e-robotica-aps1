import random
from aigyminsper.search.search_algorithms import BuscaLargura, BuscaProfundidade, BuscaProfundidadeIterativa
from aigyminsper.search.graph import State
import json

# ADICIONADO
import time
import multiprocessing
import tracemalloc
import matplotlib.pyplot as plt
import psutil

def gerar_mapa(dimensao, pct_sujeira=0.4, sujo_na_origem=False):
    total_celulas = dimensao * dimensao
    qtd_sujas = round(total_celulas * pct_sujeira)

    coordenadas = [(i, j) for i in range(dimensao) for j in range(dimensao)]

    if not sujo_na_origem:
        coordenadas.remove((0, 0))
        qtd_sujas = min(qtd_sujas, len(coordenadas))

    sujas = random.sample(coordenadas, qtd_sujas)

    matriz = [['limpo' for _ in range(dimensao)] for _ in range(dimensao)]
    for (i, j) in sujas:
        matriz[i][j] = 'sujo'

    return matriz


class AgentSpecification(State):
    def __init__(self, op, posicao, quartos, posicao_anterior=None):
            super().__init__(op)
            self.posicao = posicao
            self.quartos = quartos
            self.posicao_anterior = posicao_anterior

    def successors(self):
        successors = []

        if self.posicao[1] < len(self.quartos[0])-1:
            nova_pos = self.posicao.copy()
            nova_pos[1] += 1

            if nova_pos != self.posicao_anterior:
                obj1 = AgentSpecification(
                    'baixo',
                    nova_pos,
                    self.quartos,
                    self.posicao.copy()
                )
                successors.append(obj1)

        if self.posicao[1] > 0:
            nova_pos = self.posicao.copy()
            nova_pos[1] -= 1

            if nova_pos != self.posicao_anterior:
                obj2 = AgentSpecification(
                    'cima',
                    nova_pos,
                    self.quartos,
                    self.posicao.copy()
                )
                successors.append(obj2)

        if self.posicao[0] > 0:
            nova_pos = self.posicao.copy()
            nova_pos[0] -= 1

            if nova_pos != self.posicao_anterior:
                obj3 = AgentSpecification(
                    'esquerda',
                    nova_pos,
                    self.quartos,
                    self.posicao.copy()
                )
                successors.append(obj3)

        if self.posicao[0] < len(self.quartos)-1:
            nova_pos = self.posicao.copy()
            nova_pos[0] += 1

            if nova_pos != self.posicao_anterior:
                obj4 = AgentSpecification(
                    'direita',
                    nova_pos,
                    self.quartos,
                    self.posicao.copy()
                )
                successors.append(obj4)

        x = self.posicao[0]
        y = self.posicao[1]

        if self.quartos[x][y] == 'sujo':
            matriz = [linha.copy() for linha in self.quartos]
            matriz[x][y] = "limpo"

            obj5 = AgentSpecification(
                f'limpar coordenadas {self.posicao}',
                self.posicao.copy(),
                matriz,
                self.posicao_anterior
            )

            successors.append(obj5)

        return successors

    def is_goal(self):
        limpa = True

        for linha in self.quartos:
            if 'sujo' in linha:
                limpa = False

        pos_original = (self.posicao == [0, 0])

        return limpa and pos_original

    def description(self):
        return """Resolvendo o problema de aspirador de pó com dois quartos."""

    def cost(self):
        if "limpar" in self.operator:
            return 2
        else:
            return 1

    def env(self):
        return json.dumps(self.__dict__)


def executar_busca(nome_algoritmo, matriz, fila):

    if nome_algoritmo == "Largura":
        algoritmo = BuscaLargura()
        limite = None

    elif nome_algoritmo == "Profundidade":
        algoritmo = BuscaProfundidade()
        limite = 20

    elif nome_algoritmo == "Profundidade Iterativa":
        algoritmo = BuscaProfundidadeIterativa()
        limite = None

    nova_matriz = [linha.copy() for linha in matriz]

    state = AgentSpecification('', [0, 0], nova_matriz)

    tracemalloc.start()
    inicio = time.perf_counter()

    try:

        if limite is not None:
            result = algoritmo.search(state, limite)
        else:
            result = algoritmo.search(state)

        fim = time.perf_counter()

        memoria_atual, memoria_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tempo = fim - inicio
        memoria_mb = memoria_pico / (1024 ** 2)

        fila.put({
            "resultado": result is not None,
            "tempo": tempo,
            "memoria": memoria_mb
        })

    except Exception as erro:

        fim = time.perf_counter()

        memoria_atual, memoria_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        fila.put({
            "resultado": False,
            "tempo": fim - inicio,
            "memoria": memoria_pico / (1024 ** 2),
            "erro": str(erro)
        })


def executar_com_timeout(nome_algoritmo, matriz, timeout=300, limite_memoria_gb=16):

    fila = multiprocessing.Queue()

    processo = multiprocessing.Process(
        target=executar_busca,
        args=(nome_algoritmo, matriz, fila)
    )

    processo.start()

    inicio = time.perf_counter()

    processo_psutil = psutil.Process(processo.pid)

    limite_memoria_bytes = limite_memoria_gb * (1024 ** 3)

    while processo.is_alive():

        tempo_atual = time.perf_counter() - inicio

        if tempo_atual >= timeout:
            processo.terminate()
            processo.join()

            return {
                "status": "timeout"
            }

        try:
            memoria_atual = processo_psutil.memory_info().rss

            if memoria_atual >= limite_memoria_bytes:

                processo.terminate()
                processo.join()

                return {
                    "status": "memoria",
                    "memoria": memoria_atual / (1024 ** 3)
                }

        except psutil.NoSuchProcess:
            break
        time.sleep(0.1)

    processo.join()

    if not fila.empty():
        resultado = fila.get()
        resultado["status"] = "concluido"
        return resultado

    return {
        "status": "erro"
    }


def gerar_graficos(resultados):


    plt.figure(figsize=(10, 6))

    for algoritmo, dados in resultados.items():

        if len(dados["dimensoes"]) > 0:
            plt.plot(dados["dimensoes"], dados["tempos"], marker='o', label=algoritmo)

    plt.xlabel("Dimensão do tabuleiro (N x N)")
    plt.ylabel("Tempo de execução (segundos)")
    plt.title("Tempo de execução dos algoritmos de busca")
    plt.legend()
    plt.grid(True)

    plt.savefig("grafico_tempo.png", dpi=300, bbox_inches="tight")

    plt.show()



    plt.figure(figsize=(10, 6))

    for algoritmo, dados in resultados.items():

        if len(dados["dimensoes"]) > 0:
            plt.plot(dados["dimensoes"], dados["memorias"], marker='o', label=algoritmo)

    plt.xlabel("Dimensão do tabuleiro (N x N)")
    plt.ylabel("Pico de memória (MB)")
    plt.title("Uso de memória dos algoritmos de busca")
    plt.legend()
    plt.grid(True)

    plt.savefig("grafico_memoria.png", dpi=300, bbox_inches="tight")

    plt.show()


def main():

    dimensao = 2

    algoritmos = [
        "Largura",
        "Profundidade",
        "Profundidade Iterativa"
    ]

    resultados = {
        "Largura": {
            "dimensoes": [],
            "tempos": [],
            "memorias": []
        },
        "Profundidade": {
            "dimensoes": [],
            "tempos": [],
            "memorias": []
        },
        "Profundidade Iterativa": {
            "dimensoes": [],
            "tempos": [],
            "memorias": []
        }
    }

    ativos = {
        "Largura": True,
        "Profundidade": True,
        "Profundidade Iterativa": True
    }

    while any(ativos.values()):

        print(f'\n{"=" * 60}')
        print(f'Dimensão {dimensao}x{dimensao}')
        print(f'{"=" * 60}')

        matriz = gerar_mapa(dimensao)

        print("\nMapa:")
        for linha in matriz:
            print(linha)

        for nome_algoritmo in algoritmos:

            if not ativos[nome_algoritmo]:
                continue

            print(f'\nExecutando: {nome_algoritmo}')

            resultado = executar_com_timeout(
                nome_algoritmo,
                matriz,
                timeout=300,
                limite_memoria_gb=16
            )

            # Parou porque passou de 5 minutos
            if resultado["status"] == "timeout":
                print(
                    f'{nome_algoritmo} ultrapassou 5 minutos '
                    f'em {dimensao}x{dimensao}.'
                )

                ativos[nome_algoritmo] = False
                continue

            # Parou porque atingiu 16 GB
            elif resultado["status"] == "memoria":
                print(
                    f'{nome_algoritmo} atingiu 16 GB de memória '
                    f'em {dimensao}x{dimensao}.'
                )

                ativos[nome_algoritmo] = False
                continue

            # Algum erro inesperado
            elif resultado["status"] == "erro":
                print(
                    f'Erro durante a execução de {nome_algoritmo}.'
                )

                ativos[nome_algoritmo] = False
                continue

            # Execução terminou normalmente
            tempo = resultado["tempo"]
            memoria = resultado["memoria"]

            print(f'Tempo: {tempo:.6f} segundos')
            print(f'Pico de memória: {memoria:.4f} MB')

            if resultado["resultado"]:
                print('Achou solução!')
            else:
                print('Não achou solução.')

            resultados[nome_algoritmo]["dimensoes"].append(dimensao)
            resultados[nome_algoritmo]["tempos"].append(tempo)
            resultados[nome_algoritmo]["memorias"].append(memoria)

        dimensao += 1



    print('\n\n')
    print('=' * 70)
    print('RESULTADOS FINAIS')
    print('=' * 70)

    for algoritmo, dados in resultados.items():
        print(f'\n{algoritmo}')
        for i in range(len(dados["dimensoes"])):
            n = dados["dimensoes"][i]
            tempo = dados["tempos"][i]
            memoria = dados["memorias"][i]
            print(f'{n}x{n}: {tempo:.6f} segundos | {memoria:.4f} MB')

        if dados["dimensoes"]:

            ultimo = dados["dimensoes"][-1]
            print(f'Último tabuleiro concluído: {ultimo}x{ultimo}')

    gerar_graficos(resultados)


if __name__ == '__main__':
    multiprocessing.freeze_support()

    main()