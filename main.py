from services import lerArquivoSTRIPS, processarAcoes, converter_para_vetor, criarEstado
import solvers
import time
import os
from concurrent.futures import ProcessPoolExecutor, TimeoutError


def executar_algoritmo_wrapper(nome_algoritmo, func, estado_inicial, objetivos, acoes):
    inicio = time.time()
    try:
        resultado, espaco_mb = func(estado_inicial, objetivos, acoes)
        fim = time.time()

        tempo = fim - inicio
        passos = len(resultado) if resultado else 0

        return {
            'algoritmo': nome_algoritmo,
            'sucesso': resultado is not None,
            'passos': passos,
            'tempo': tempo,
            'espaco_mb': espaco_mb,
            'caminho': resultado
        }
    except Exception as e:
        return {
            'algoritmo': nome_algoritmo,
            'sucesso': False,
            'erro': str(e)
        }


def run_iddfs(estado, objetivos, acoes):
    return solvers.busca_profundidade_iterativa(estado, objetivos, acoes, 50)


def run_dls(estado, objetivos, acoes):
    medidor = solvers.MedidorEspaco()
    resultado = solvers.busca_profundidade_limitada(
        estado, objetivos, acoes, 50, set(), medidor
    )
    return resultado, medidor.espaco_mb()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        caminho_arquivo = sys.argv[1]
    else:
        caminho_arquivo = 'planningsat/planningsat/blocks-4-0.strips' # pode alterar

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo {caminho_arquivo} não encontrado.")
        exit()

    print(f'Carregando problema: {caminho_arquivo}')
    listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos, estadoInicial, estadoObjetivo = lerArquivoSTRIPS(caminho_arquivo)
    dicionarioAcoes = processarAcoes(listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos)

    proposicao_para_indice, indice_para_proposicao, inicial_indices, objetivo_indices = converter_para_vetor(
        dicionarioAcoes, estadoInicial, estadoObjetivo
    )

    estado_inicial_obj = criarEstado(inicial_indices)

    print(f"Estado Inicial possui {len(inicial_indices)} proposições ativas.")
    print(f"Objetivo requer {len(objetivo_indices)} proposições.")

    tarefas = [
        ('Busca em Largura (BFS)', solvers.busca_em_largura),
        ('A* (A-Star)', solvers.busca_a_star),
        ('DLS', run_dls),
        ('IDDFS (Lim=50)', run_iddfs)
    ]

    print(f"\nIniciando execução paralela de {len(tarefas)} algoritmos usando multiprocessamento...")
    print("Aguarde... (algoritmos mais pesados podem demorar)\n")

    with ProcessPoolExecutor() as executor:
        futures = []
        for nome, func in tarefas:
            futures.append(
                executor.submit(
                    executar_algoritmo_wrapper,
                    nome,
                    func,
                    estado_inicial_obj,
                    objetivo_indices,
                    dicionarioAcoes
                )
            )

        for future in futures:
            try:
                res = future.result(timeout=7200)  # 2 horas para timeout
                print("-" * 60)
                print(f"Algoritmo: {res['algoritmo']}")

                if res.get('erro'):
                    print(f"Status: ERRO ({res['erro']})")

                elif res['sucesso']:
                    print("Status: SUCESSO")
                    print(f"Tempo: {res['tempo']:.4f} segundos")
                    print(f"Espaço (aprox.): {res['espaco_mb']:.4f} MB")
                    print(f"Comprimento da Solução: {res['passos']} ações")

                else:
                    print("Status: FALHA / Não encontrou solução ou atingiu limite")

            except TimeoutError:
                print("-" * 60)
                print(f"Algoritmo: {res.get('algoritmo', 'DESCONHECIDO') if 'res' in locals() else 'DESCONHECIDO'}")
                print("Status: TIMEOUT (2 horas excedidas)")

