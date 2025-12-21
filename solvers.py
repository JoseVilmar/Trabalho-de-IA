import heapq
from collections import deque, defaultdict
from services import sucessores, objetivo
import time


BYTES_POR_ELEMENTO = 32
BYTES_PARA_MB = 1024 * 1024
TIMEOUT = 'timeout'


_prop_to_actions = defaultdict(list)
_action_pre_count = {}

def inicializar_heuristicas(dicionario_acoes):
    _prop_to_actions.clear()
    _action_pre_count.clear()

    for acao in dicionario_acoes.values():
        _action_pre_count[acao.nome] = len(acao.pre_idx)
        for pre in acao.pre_idx:
            _prop_to_actions[pre].append(acao)

def heuristica(estado, objetivos_indices, dicionario_acoes):
    h_vals = {}
    pq = []

    action_unsat = {}
    action_accum = defaultdict(int)

    for p in estado.proposicoes:
        h_vals[p] = 0
        heapq.heappush(pq, (0, p))

    while pq:
        custo_p, p = heapq.heappop(pq)

        if custo_p > h_vals.get(p, float('inf')):
            continue

        for acao in _prop_to_actions.get(p, []):
            nome = acao.nome

            if nome not in action_unsat:
                action_unsat[nome] = _action_pre_count[nome]

            action_unsat[nome] -= 1
            action_accum[nome] = max(action_accum[nome], custo_p)

            if action_unsat[nome] == 0:
                custo_acao = 1 + action_accum[nome]
                for eff in acao.eff_pos_idx:
                    if custo_acao < h_vals.get(eff, float('inf')):
                        h_vals[eff] = custo_acao
                        heapq.heappush(pq, (custo_acao, eff))

    max_custo = 0
    for obj in objetivos_indices:
        val = h_vals.get(obj, float('inf'))
        if val == float('inf'):
            return float('inf')
        max_custo = max(max_custo, val)

    return max_custo


def busca_em_largura(estado_inicial, objetivos_indices, dicionario_acoes):
    fila = deque([estado_inicial])
    visitados = set([estado_inicial.mascara])

    medidor = MedidorEspaco()
    controle = ControleTempo(7200)

    medidor.atualizar(fila, visitados)

    while fila:
        if controle.estourou():
            return TIMEOUT, medidor.espaco_mb()

        estado_atual = fila.popleft()

        if objetivo(estado_atual, objetivos_indices):
            return reconstruir_caminho(estado_atual), medidor.espaco_mb()

        for filho in sucessores(estado_atual, dicionario_acoes):
            if filho.mascara not in visitados:
                visitados.add(filho.mascara)
                fila.append(filho)
                medidor.atualizar(fila, visitados)

    return None, medidor.espaco_mb()


def busca_profundidade_limitada(
    estado, objetivos_indices, dicionario_acoes, limite,
    visitados_profundidade, medidor, controle
):
    if controle.estourou():
        return TIMEOUT

    medidor.atualizar(visitados_profundidade)

    if objetivo(estado, objetivos_indices):
        return reconstruir_caminho(estado)

    if limite <= 0:
        return 'corte'

    corte_ocorreu = False
    mascara = estado.mascara
    visitados_profundidade.add(mascara)

    try:
        for filho in sucessores(estado, dicionario_acoes):
            if filho.mascara not in visitados_profundidade:
                resultado = busca_profundidade_limitada(
                    filho, objetivos_indices, dicionario_acoes,
                    limite - 1, visitados_profundidade, medidor, controle
                )

                if resultado == TIMEOUT:
                    return TIMEOUT
                if resultado == 'corte':
                    corte_ocorreu = True
                elif resultado is not None:
                    return resultado
    finally:
        visitados_profundidade.remove(mascara)

    return 'corte' if corte_ocorreu else None


def busca_profundidade_iterativa(
    estado_inicial, objetivos_indices, dicionario_acoes, profundidade_maxima=100
):
    medidor = MedidorEspaco()
    controle = ControleTempo(7200)

    for limite in range(profundidade_maxima):
        if controle.estourou():
            return TIMEOUT, medidor.espaco_mb()

        resultado = busca_profundidade_limitada(
            estado_inicial, objetivos_indices, dicionario_acoes,
            limite, set(), medidor, controle
        )

        if resultado == TIMEOUT:
            return TIMEOUT, medidor.espaco_mb()

        if resultado != 'corte' and resultado is not None:
            return resultado, medidor.espaco_mb()

        if resultado is None:
            return None, medidor.espaco_mb()

    return None, medidor.espaco_mb()


class NoAStar:
    def __init__(self, estado, g, h):
        self.estado = estado
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f

def busca_a_star(estado_inicial, objetivos_indices, dicionario_acoes):
    inicializar_heuristicas(dicionario_acoes)

    fila_prioridade = []
    custos_g = {}

    medidor = MedidorEspaco()
    controle = ControleTempo(7200)

    h0 = heuristica(estado_inicial, objetivos_indices, dicionario_acoes)
    heapq.heappush(fila_prioridade, NoAStar(estado_inicial, 0, h0))
    custos_g[estado_inicial.mascara] = 0

    medidor.atualizar(fila_prioridade, custos_g)

    while fila_prioridade:
        if controle.estourou():
            return TIMEOUT, medidor.espaco_mb()

        no_atual = heapq.heappop(fila_prioridade)
        estado_atual = no_atual.estado

        if no_atual.g > custos_g[estado_atual.mascara]:
            continue

        if objetivo(estado_atual, objetivos_indices):
            return reconstruir_caminho(estado_atual), medidor.espaco_mb()

        for filho in sucessores(estado_atual, dicionario_acoes):
            novo_g = no_atual.g + 1
            mascara = filho.mascara

            if mascara not in custos_g or novo_g < custos_g[mascara]:
                custos_g[mascara] = novo_g
                h = heuristica(filho, objetivos_indices, dicionario_acoes)
                heapq.heappush(fila_prioridade, NoAStar(filho, novo_g, h))
                medidor.atualizar(fila_prioridade, custos_g)

    return None, medidor.espaco_mb()


def reconstruir_caminho(estado):
    caminho = []
    atual = estado
    while atual.pai is not None:
        caminho.append(atual.acaoUsada)
        atual = atual.pai
    return list(reversed(caminho))


class MedidorEspaco:
    def __init__(self):
        self.max_elementos = 0

    def atualizar(self, *estruturas):
        total = sum(len(e) for e in estruturas)
        self.max_elementos = max(self.max_elementos, total)

    def espaco_bytes(self):
        return self.max_elementos * BYTES_POR_ELEMENTO

    def espaco_mb(self):
        return self.espaco_bytes() / BYTES_PARA_MB


class ControleTempo:
    def __init__(self, tempo_max):
        self.inicio = time.time()
        self.tempo_max = tempo_max

    def estourou(self):
        return time.time() - self.inicio > self.tempo_max
