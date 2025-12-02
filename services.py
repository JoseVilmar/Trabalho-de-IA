# Lê o arquivo STRIPS de acordo com o formato especifico das entradas dadas pelo professor
def lerArquivoSTRIPS(caminho):
    with open(caminho, 'r') as arquivo:
        listaAcoes = []
        dicionarioPrecondicoes = {}
        dicionarioEfeitos = {}

        linha_atual = arquivo.readline().strip()

        while linha_atual:
            nomeAcao = linha_atual
            precondicoes = arquivo.readline().strip().split(";")
            efeitos = arquivo.readline().strip().split(";")

            listaAcoes.append(nomeAcao)
            dicionarioPrecondicoes[nomeAcao] = precondicoes
            dicionarioEfeitos[nomeAcao] = efeitos

            linha_atual = arquivo.readline().strip()

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
        self.pre_pos_idx = set()
        self.pre_neg_idx = set()
        self.eff_pos_idx = set()
        self.eff_neg_idx = set()

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

    for aux in acao.eff_neg_idx:
        novo.proposicoes.discard(aux)

    for aux in acao.eff_pos_idx:
        novo.proposicoes.add(aux)

    novo.pai = estado
    novo.acaoUsada = acao.nome
    novo.custo = estado.custo + acao.custo

    return novo

# Função para gerar sucessores de um estado
def sucessores(estado, dicionarioAcoes):
    lista = []

    for acao in dicionarioAcoes.values():
        if acao.pre_pos_idx.issubset(estado.proposicoes) and acao.pre_neg_idx.isdisjoint(estado.proposicoes):
            novoEstado = aplicarAcao(estado, acao)
            lista.append(novoEstado)

    return lista

def objetivo(estado, objetivo_indices):
    return objetivo_indices.issubset(estado.proposicoes)

# Função para converter proposições para representação vetorial
def converter_para_vetor(dicionarioAcoes, estadoInicial, estadoObjetivo):
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
            proposicoes.add(proposicao)

    indice_para_proposicao = sorted(proposicoes)
    proposicao_para_indice = {p: i for i, p in enumerate(indice_para_proposicao)}

    for acao in dicionarioAcoes.values():
        acao.pre_pos_idx = set()
        acao.pre_neg_idx = set()
        acao.eff_pos_idx = set()
        acao.eff_neg_idx = set()

        for precondicao in acao.precondicoes:
            if not precondicao:
                continue
            if precondicao.startswith('~'):
                chave = precondicao[1:]
                if chave in proposicao_para_indice:
                    acao.pre_neg_idx.add(proposicao_para_indice[chave])
            else:
                if precondicao in proposicao_para_indice:
                    acao.pre_pos_idx.add(proposicao_para_indice[precondicao])

        for efeito in acao.efeitosPositivos:
            if efeito in proposicao_para_indice:
                acao.eff_pos_idx.add(proposicao_para_indice[efeito])

        for efeito in acao.efeitosNegativos:
            if efeito in proposicao_para_indice:
                acao.eff_neg_idx.add(proposicao_para_indice[efeito])

    inicial_indices = set()
    objetivo_indices = set()

    for proposicao in estadoInicial:
        if proposicao and proposicao in proposicao_para_indice:
            inicial_indices.add(proposicao_para_indice[proposicao])

    for proposicao in estadoObjetivo:
        if proposicao and proposicao in proposicao_para_indice:
            objetivo_indices.add(proposicao_para_indice[proposicao])

    return proposicao_para_indice, indice_para_proposicao, inicial_indices, objetivo_indices
