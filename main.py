from services import lerArquivoSTRIPS, processarAcoes, converter_para_vetor, criarEstado

if __name__ == '__main__':
    # Carregar arquivo STRIPS
    caminho = 'planningsat/planningsat/blocks-4-0.strips'
    print(f'Carregando: {caminho}')
    
    listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos, estadoInicial, estadoObjetivo = lerArquivoSTRIPS(caminho)
    dicionarioAcoes = processarAcoes(listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos)

    # Converter para representação vetorial
    proposicao_para_indice, indice_para_proposicao, vetor_estado_inicial, vetor_estado_objetivo = converter_para_vetor(
        dicionarioAcoes, estadoInicial, estadoObjetivo
    )

    # Converter estado inicial (strings) para conjunto de índices inteiros e criar Estado
    estado_inicial_indices = set()
    for proposicao in estadoInicial:
        if not proposicao:
            continue
        # apenas proposições positivas são armazenadas no conjunto (negadas significam ausência)
        if proposicao.startswith('~'):
            continue
        if proposicao in proposicao_para_indice:
            estado_inicial_indices.add(proposicao_para_indice[proposicao])

    estadoInicial = criarEstado(estado_inicial_indices)

    objetivo_indices = set()
    for proposicao in estadoObjetivo:
        if proposicao and not proposicao.startswith('~') and proposicao in proposicao_para_indice:
            objetivo_indices.add(proposicao_para_indice[proposicao])

    estadoObjetivo = criarEstado(objetivo_indices)

    # Exibir informações
    print(f'\nTotal de proposições: {len(indice_para_proposicao)}')
    print('\nProposições (índice -> proposição):')
    for indice, proposicao in enumerate(indice_para_proposicao):
        print(f'{indice:2d}: {proposicao}')

    # Imprimir apenas índices com valor não-zero (1 ou -1)
    indices_estado_inicial = [i for i, v in enumerate(vetor_estado_inicial) if v != 0]
    indices_estado_objetivo = [i for i, v in enumerate(vetor_estado_objetivo) if v != 0]
    
    print(f'\nEstado inicial: {indices_estado_inicial}')
    print(f'Estado objetivo: {indices_estado_objetivo}')

    # Demonstração: verificar primeira ação
    primeira_acao = next(iter(dicionarioAcoes.values()))
    print(f'\nPrimeira ação: {primeira_acao.nome}')
    print(f'  Precondições: {primeira_acao.precondicoes}')
    print(f'  Efeitos positivos: {primeira_acao.efeitosPositivos}')
    print(f'  Efeitos negativos: {primeira_acao.efeitosNegativos}')
    print(f'  Índices precondicões: {primeira_acao.indices_precondicoes}')
    print(f'  Índices efeitos positivos: {primeira_acao.indices_efeitos_positivos}')
