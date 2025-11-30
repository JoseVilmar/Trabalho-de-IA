# Lê o arquivo STRIPS de acordo com o formato especifico das entradas dadas pelo professor
def lerArquivoSTRIPS(caminho):
    with open(caminho, 'r') as arquivo:
        listaAcoes = []
        dicionarioPrecondicoes = {}
        dicionarioEfeitos = {}

        linha_atual = arquivo.readline().strip()

        # Ler ações, precondições e efeitos
        while linha_atual:
            nomeAcao = linha_atual
            precondicoes = arquivo.readline().strip().split(";")
            efeitos = arquivo.readline().strip().split(";")

            listaAcoes.append(nomeAcao)
            dicionarioPrecondicoes[nomeAcao] = precondicoes
            dicionarioEfeitos[nomeAcao] = efeitos

            linha_atual = arquivo.readline().strip()

        # Ler estado inicial e objetivo
        linhaInicial = arquivo.readline().strip()
        linhaObjetivo = arquivo.readline().strip()

        estadoInicial = linhaInicial.split(";")
        estadoObjetivo = linhaObjetivo.split(";")

        return (listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos,
                estadoInicial, estadoObjetivo)

#Estrutura de dados para representar um estado no espaço de busca
class Estado:
    def __init__(self, proposicoes=None):
        self.proposicoes = set(proposicoes) if proposicoes is not None else set()
        self.pai = None
        self.acaoUsada = None
        self.custo = 0

# Função para criar um novo estado
def criarEstado(proposicoes=None):
    return Estado(proposicoes)

# Estrutura de dados para representar uma ação
class Acao:
    def __init__(self):
        self.nome = ""
        self.precondicoes = set()
        self.efeitosPositivos = set()
        self.efeitosNegativos = set()
        self.custo = 1

# Função para processar ações/criar dicionário de ações
def processarAcoes(listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos):
    dicionarioAcoes = {}

    for nome in listaAcoes:
        precondicoes = dicionarioPrecondicoes[nome]
        efeitos = dicionarioEfeitos[nome]

        novaAcao = Acao()
        novaAcao.nome = nome
        novaAcao.precondicoes = set(precondicoes)
        novaAcao.efeitosPositivos = set()
        novaAcao.efeitosNegativos = set()
        novaAcao.custo = 1

        for efeito in efeitos:
            if efeito.startswith("~"):
                novaAcao.efeitosNegativos.add(efeito[1:])
            else:
                novaAcao.efeitosPositivos.add(efeito)
                novaAcao.custo += 1

        dicionarioAcoes[nome] = novaAcao

    return dicionarioAcoes

# Função para aplicar uma ação a um estado
def aplicarAcao(estado, acao):
    novo = criarEstado(list(estado.proposicoes))

    # Remover efeitos negativos (índices)
    for aux in getattr(acao, 'indices_efeitos_negativos', []):
        novo.proposicoes.discard(aux)

    # Adicionar efeitos positivos (índices)
    for aux in getattr(acao, 'indices_efeitos_positivos', []):
        novo.proposicoes.add(aux)

    novo.pai = estado
    novo.acaoUsada = acao.nome
    novo.custo = estado.custo + acao.custo

    return novo

# Função para gerar sucessores de um estado
def sucessores(estado, dicionarioAcoes):
    lista = []

    for acao in dicionarioAcoes.values():
        # Obter índices precondições positivas e negativas
        indices_pos = getattr(acao, 'indices_precondicoes', [])
        indices_neg = getattr(acao, 'indices_precondicoes_negadas', [])

        # Verifica que todas as precondições positivas estão presentes
        aplicavel = True
        for aux in indices_pos:
            if aux not in estado.proposicoes:
                aplicavel = False
                break

        # Verifica que todas as precondições negadas NÃO estão presentes
        if aplicavel:
            for aux in indices_neg:
                if aux in estado.proposicoes:
                    aplicavel = False
                    break

        if aplicavel:
            novoEstado = aplicarAcao(estado, acao)
            lista.append(novoEstado)

    return lista

# Função para verificar se o estado satisfaz o objetivo
def Objetivo(estado, objetivo, proposicao_para_indice):

    for proposicao in objetivo:
        if not proposicao:
            continue

        if proposicao.startswith('~'):
            chave = proposicao[1:]

            if chave in proposicao_para_indice:
                aux = proposicao_para_indice[chave]

                if aux in estado.proposicoes:
                    return False
            else:
                # proposição de objetivo desconhecida -> tratar como não satisfeita
                return False
        else:
            if proposicao in proposicao_para_indice:
                aux = proposicao_para_indice[proposicao]
                if aux not in estado.proposicoes:
                    return False
            else:
                return False
    return True

# Função para converter proposições para representação vetorial
def converter_para_vetor(dicionarioAcoes, estadoInicial, estadoObjetivo):
    # Coletar todas as proposições (normalizando '~')
    proposicoes = set()
    
    for acao in dicionarioAcoes.values():
        for precondicao in acao.precondicoes:
            if precondicao:
                chave = precondicao[1:] if precondicao.startswith('~') else precondicao
                proposicoes.add(chave)

        for efeito in acao.efeitosPositivos:
            if efeito:
                proposicoes.add(efeito)

        for efeito in acao.efeitosNegativos:
            if efeito:
                proposicoes.add(efeito)
    
    for proposicao in estadoInicial + estadoObjetivo:
        if proposicao:
            chave = proposicao[1:] if proposicao.startswith('~') else proposicao
            proposicoes.add(chave)

    # Criar mapeamentos
    indice_para_proposicao = sorted(proposicoes)
    proposicao_para_indice = {p: i for i, p in enumerate(indice_para_proposicao)}

    # Pré-computar índices em cada ação
    for acao in dicionarioAcoes.values():
        acao.indices_precondicoes = []
        acao.indices_precondicoes_negadas = []
        acao.indices_efeitos_positivos = []
        acao.indices_efeitos_negativos = []

        for precondicao in acao.precondicoes:
            if not precondicao:
                continue
            if precondicao.startswith('~'):
                chave = precondicao[1:]
                if chave in proposicao_para_indice:
                    acao.indices_precondicoes_negadas.append(proposicao_para_indice[chave])
            else:
                if precondicao in proposicao_para_indice:
                    acao.indices_precondicoes.append(proposicao_para_indice[precondicao])

        for efeito in acao.efeitosPositivos:
            if efeito in proposicao_para_indice:
                acao.indices_efeitos_positivos.append(proposicao_para_indice[efeito])
        
        for efeito in acao.efeitosNegativos:
            if efeito in proposicao_para_indice:
                acao.indices_efeitos_negativos.append(proposicao_para_indice[efeito])

    # Criar vetores de estado
    tamanho = len(proposicao_para_indice)
    vetor_estado_inicial = [0] * tamanho
    vetor_estado_objetivo = [0] * tamanho
    
    for proposicao in estadoInicial:
        if not proposicao:
            continue
        if proposicao.startswith('~'):
            chave = proposicao[1:]
            valor = -1
        else:
            chave = proposicao
            valor = 1
        if chave in proposicao_para_indice:
            vetor_estado_inicial[proposicao_para_indice[chave]] = valor
    
    for proposicao in estadoObjetivo:
        if not proposicao:
            continue
        if proposicao.startswith('~'):
            chave = proposicao[1:]
            valor = -1
        else:
            chave = proposicao
            valor = 1
        if chave in proposicao_para_indice:
            vetor_estado_objetivo[proposicao_para_indice[chave]] = valor

    for acao in dicionarioAcoes.values():
        acao.set_precondicoes = set(acao.indices_precondicoes)
        acao.set_precondicoes_negadas = set(acao.indices_precondicoes_negadas)
        acao.set_efeitos_pos = set(acao.indices_efeitos_positivos)
        acao.set_efeitos_neg = set(acao.indices_efeitos_negativos)

    return proposicao_para_indice, indice_para_proposicao, vetor_estado_inicial, vetor_estado_objetivo
