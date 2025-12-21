# Trabalho-de-IA
# Planejador STRIPS com Otimizações Avançadas

Este projeto implementa um planejador para problemas definidos no formato STRIPS, utilizando diversos algoritmos de busca e técnicas avançadas de otimização para performance.

## 🚀 Algoritmos Implementados

O sistema executa os seguintes algoritmos em paralelo para comparação:

1.  **Busca em Largura (BFS)**: Garante a solução ótima (menor número de ações), mas explora muitos estados.
2.  **A-Star**: Utiliza a heurística `h_max` para guiar a busca. É o algoritmo mais eficiente para este domínio.
3.  **IDDFS (Iterative Deepening DFS)**: Busca em profundidade com limite iterativo. Otimizado com backtracking para baixo consumo de memória.

## 🧠 Heurística: `h_max` (Aditiva)

Para o algoritmo A*, implementamos a heurística **`h_max`** (Additive Heuristic).
*   **Conceito**: Estima o custo para alcançar o objetivo somando os custos de alcançar cada submeta individualmente em um problema relaxado (onde os efeitos negativos das ações são ignorados).
*   **Implementação**: Utilizamos uma abordagem baseada em **Dijkstra** sobre o Grafo de Planejamento Relaxado (RPG). Isso propaga os custos de forma eficiente, evitando iterações desnecessárias sobre ações irrelevantes.

## ⚡ Otimizações de Performance

Para lidar com problemas maiores (como `blocks-10-0` e superiores), aplicamos otimizações profundas em Python:

### 1. Bitmasks (Máscaras de Bits)
*   **Problema**: Operações de conjunto (`set.issubset`, `set.intersection`) são lentas quando executadas milhões de vezes.
*   **Solução**: Convertemos o estado e as pré-condições das ações para **inteiros (bitmasks)**.
*   **Ganho**: Verificações de aplicabilidade de ação (`(estado & pre) == pre`) tornaram-se extremamente rápidas, reduzindo o tempo de expansão de nós.

### 2. Backtracking no IDDFS
*   **Problema**: Criar cópias do conjunto de visitados (`set.copy()`) a cada passo da recursão consome muita memória e tempo.
*   **Solução**: Usamos uma única estrutura de dados e aplicamos/desfazemos mudanças (backtracking) ao entrar e sair da recursão.

### 3. Multiprocessamento
*   Utilizamos `ProcessPoolExecutor` para rodar os algoritmos em núcleos separados da CPU, permitindo que todos competam em tempo real sem serem bloqueados pelo GIL do Python.

## 📂 Estrutura do Código

*   `main.py`: Ponto de entrada. Carrega o problema, configura os processos e exibe os resultados.
*   `solvers.py`: Implementação dos algoritmos de busca (A*, BFS, IDDFS, DLS) e da heurística `h_max`.
*   `services.py`: Gerenciamento de estado, leitura de arquivos STRIPS e lógica de sucessores com otimização de bitmasks.

## 🛠️ Como Executar

1.  Certifique-se de ter Python 3.10+ instalado.
2.  Edite o arquivo `main.py` para escolher o problema desejado na variável `caminho_arquivo`.
3.  Execute:

```bash
python3 main.py
```

## 📊 Resultados Esperados

Em testes com problemas do domínio Blocks World:
*   **blocks-5-0**: Resolvido em < 0.01s por todos os algoritmos.
*   **blocks-7-0**: A* resolve em ~0.015s, enquanto BFS leva ~0.75s (A* é ~50x mais rápido).
