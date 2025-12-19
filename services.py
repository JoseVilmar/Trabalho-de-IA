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


class Estado:
    def __init__(self, proposicoes=None, mascara=0):
        self.proposicoes = set(proposicoes) if proposicoes is not None else set()
        self.mascara = mascara
        self.pai = None
        self.acaoUsada = None


def criarEstado(proposicoes=None):
    mascara = 0
    if proposicoes:
        for p in proposicoes:
            mascara |= (1 << p)
    return Estado(proposicoes, mascara)


class Acao:
    def __init__(self):
        self.nome = ""
        self.precondicoes = set()
        self.efeitosPositivos = set()
        self.efeitosNegativos = set()

        self.pre_idx = set()
        self.eff_pos_idx = set()
        self.eff_neg_idx = set()

        self.pre_mask = 0
        self.eff_pos_mask = 0
        self.eff_neg_mask = 0


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

        for efeito in efeitos:
            if efeito.startswith("~"):
                novaAcao.efeitosNegativos.add(efeito[1:])
            else:
                novaAcao.efeitosPositivos.add(efeito)

        dicionarioAcoes[nome] = novaAcao

    return dicionarioAcoes


def aplicarAcao(estado, acao):
    novo_proposicoes = estado.proposicoes.copy()

    for idx in acao.eff_neg_idx:
        novo_proposicoes.discard(idx)

    for idx in acao.eff_pos_idx:
        novo_proposicoes.add(idx)

    nova_mascara = estado.mascara
    nova_mascara &= ~acao.eff_neg_mask
    nova_mascara |= acao.eff_pos_mask

    novo = Estado(novo_proposicoes, nova_mascara)
    novo.pai = estado
    novo.acaoUsada = acao.nome

    return novo


def sucessores(estado, dicionarioAcoes):
    lista = []
    mascara_estado = estado.mascara

    for acao in dicionarioAcoes.values():
        if (mascara_estado & acao.pre_mask) == acao.pre_mask:
            novoEstado = aplicarAcao(estado, acao)
            lista.append(novoEstado)

    return lista


def objetivo(estado, objetivo_indices):
    return objetivo_indices.issubset(estado.proposicoes)


def converter_para_vetor(dicionarioAcoes, estadoInicial, estadoObjetivo):
    proposicoes = set()

    for acao in dicionarioAcoes.values():
        for precondicao in acao.precondicoes:
            if precondicao:
                proposicoes.add(precondicao)

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
        acao.pre_idx = set()
        acao.eff_pos_idx = set()
        acao.eff_neg_idx = set()
        
        acao.pre_mask = 0
        acao.eff_pos_mask = 0
        acao.eff_neg_mask = 0

        for precondicao in acao.precondicoes:
            if not precondicao:
                continue

            if precondicao in proposicao_para_indice:
                idx = proposicao_para_indice[precondicao]
                acao.pre_idx.add(idx)
                acao.pre_mask |= (1 << idx)

        for efeito in acao.efeitosPositivos:
            if efeito in proposicao_para_indice:
                idx = proposicao_para_indice[efeito]
                acao.eff_pos_idx.add(idx)
                acao.eff_pos_mask |= (1 << idx)

        for efeito in acao.efeitosNegativos:
            if efeito in proposicao_para_indice:
                idx = proposicao_para_indice[efeito]
                acao.eff_neg_idx.add(idx)
                acao.eff_neg_mask |= (1 << idx)

    inicial_indices = set()
    objetivo_indices = set()

    for proposicao in estadoInicial:
        if proposicao and proposicao in proposicao_para_indice:
            inicial_indices.add(proposicao_para_indice[proposicao])

    for proposicao in estadoObjetivo:
        if proposicao and proposicao in proposicao_para_indice:
            objetivo_indices.add(proposicao_para_indice[proposicao])

    return proposicao_para_indice, indice_para_proposicao, inicial_indices, objetivo_indices
