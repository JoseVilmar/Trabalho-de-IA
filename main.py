from services import lerArquivoSTRIPS, processarAcoes, converter_para_vetor, criarEstado

if __name__ == '__main__':
    caminho = 'planningsat/planningsat/blocks-4-0.strips'
    print(f'Carregando: {caminho}')

    listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos, estadoInicial, estadoObjetivo = lerArquivoSTRIPS(caminho)
    dicionarioAcoes = processarAcoes(listaAcoes, dicionarioPrecondicoes, dicionarioEfeitos)

    proposicao_para_indice, indice_para_proposicao, inicial_indices, objetivo_indices = converter_para_vetor(
        dicionarioAcoes, estadoInicial, estadoObjetivo
    )

    estado = criarEstado(inicial_indices)

    print(f'\nTotal de proposições: {len(indice_para_proposicao)}')
    print('\nProposições (índice -> proposição):')
    for indice, proposicao in enumerate(indice_para_proposicao):
        print(f'{indice:2d}: {proposicao}')

    print(f'\nEstado inicial: {sorted(inicial_indices)}')
    print(f'Estado objetivo: {sorted(objetivo_indices)}')

    primeira_acao = next(iter(dicionarioAcoes.values()))
    print(f'\nPrimeira ação: {primeira_acao.nome}')
    print(f'  Precondições: {primeira_acao.precondicoes}')
    print(f'  Efeitos positivos: {primeira_acao.efeitosPositivos}')
    print(f'  Efeitos negativos: {primeira_acao.efeitosNegativos}')
    print(f'  Índices precondicões (pos/neg): {sorted(primeira_acao.pre_pos_idx)}, {sorted(primeira_acao.pre_neg_idx)}')
    print(f'  Índices efeitos (pos/neg): {sorted(primeira_acao.eff_pos_idx)}, {sorted(primeira_acao.eff_neg_idx)}')
