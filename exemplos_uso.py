"""
Exemplos de uso do RKO-BRKGA para diferentes cenários

Este arquivo demonstra como usar o algoritmo em situações práticas
"""

import numpy as np
from alwabp_instance import ALWABPInstance
from rko_brkga import RKO_BRKGA
from visualization import (visualize_solution, visualize_precedence_graph,
                          visualize_worker_capabilities, compare_solutions)


def exemplo_1_linha_simples():
    """
    Exemplo 1: Linha de produção simples com 4 estações
    
    Cenário: Montagem de produtos eletrônicos simples
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 1: LINHA DE PRODUÇÃO SIMPLES")
    print("=" * 80)
    print("\nCenário: Montagem de produtos eletrônicos")
    print("- 6 tarefas sequenciais")
    print("- 3 trabalhadores com diferentes habilidades")
    print("- 3 estações de trabalho")
    
    # Criar instância
    instance = ALWABPInstance(n_tasks=6, n_workers=3, n_stations=3)
    
    # Tempos de execução (em minutos)
    # Trabalhador 0: experiente em todas as tarefas
    # Trabalhador 1: bom em tarefas iniciais
    # Trabalhador 2: bom em tarefas finais
    instance.execution_times = np.array([
        [4, 5, 4, 5, 4, 5],  # Trabalhador 0 (experiente)
        [3, 4, 5, 6, 7, 8],  # Trabalhador 1 (bom no início)
        [8, 7, 6, 5, 4, 3],  # Trabalhador 2 (bom no fim)
    ], dtype=float)
    
    # Precedências: sequência linear 0→1→2→3→4→5
    for i in range(5):
        instance.add_precedence(i, i + 1)
    
    # Visualizar informações da instância
    visualize_precedence_graph(instance)
    visualize_worker_capabilities(instance)
    
    # Resolver
    print("\n[EXECUTANDO ALGORITMO...]")
    rko = RKO_BRKGA(instance, population_size=50, elite_size=0.2)
    solution, _ = rko.solve(brkga_generations=50, verbose=False)
    
    # Visualizar solução
    visualize_solution(solution, instance)
    
    return solution, instance


def exemplo_2_trabalhadores_especializados():
    """
    Exemplo 2: Trabalhadores com especializações diferentes
    
    Cenário: Linha com tarefas que exigem habilidades específicas
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: TRABALHADORES ESPECIALIZADOS")
    print("=" * 80)
    print("\nCenário: Montagem com tarefas especializadas")
    print("- 10 tarefas com 2 cadeias paralelas")
    print("- 4 trabalhadores, cada um especializado em certas tarefas")
    print("- 4 estações de trabalho")
    
    # Criar instância
    instance = ALWABPInstance(n_tasks=10, n_workers=4, n_stations=4)
    
    # Tempos base
    base_times = np.random.uniform(5, 10, (4, 10))
    
    # Especializar trabalhadores
    # Trabalhador 0: especialista em tarefas 0-2 (reduz tempo em 50%)
    base_times[0, 0:3] *= 0.5
    
    # Trabalhador 1: especialista em tarefas 3-5
    base_times[1, 3:6] *= 0.5
    
    # Trabalhador 2: especialista em tarefas 6-7
    base_times[2, 6:8] *= 0.5
    
    # Trabalhador 3: especialista em tarefas 8-9
    base_times[3, 8:10] *= 0.5
    
    instance.execution_times = base_times
    
    # Precedências: duas cadeias paralelas
    # Cadeia 1: 0→1→2→3→4
    # Cadeia 2: 5→6→7→8→9
    for i in range(4):
        instance.add_precedence(i, i + 1)
        instance.add_precedence(i + 5, i + 6)
    
    # Algumas incompatibilidades (tarefas muito especializadas)
    instance.set_incompatible_task(1, 0)  # Trab. 1 não pode fazer tarefa 0
    instance.set_incompatible_task(0, 9)  # Trab. 0 não pode fazer tarefa 9
    
    # Visualizar informações
    visualize_worker_capabilities(instance)
    
    # Resolver
    print("\n[EXECUTANDO ALGORITMO...]")
    rko = RKO_BRKGA(instance, population_size=80)
    solution, _ = rko.solve(brkga_generations=70, verbose=False)
    
    # Visualizar solução
    visualize_solution(solution, instance)
    
    return solution, instance


def exemplo_3_grafo_complexo():
    """
    Exemplo 3: Grafo de precedências complexo
    
    Cenário: Montagem com múltiplas dependências entre tarefas
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: PRECEDÊNCIAS COMPLEXAS")
    print("=" * 80)
    print("\nCenário: Montagem de produto complexo")
    print("- 12 tarefas com grafo de precedências tipo 'diamante'")
    print("- 4 trabalhadores com habilidades balanceadas")
    print("- 4 estações de trabalho")
    
    # Criar instância
    instance = ALWABPInstance(n_tasks=12, n_workers=4, n_stations=4)
    
    # Tempos balanceados com variação
    np.random.seed(42)
    instance.execution_times = np.random.uniform(3, 8, (4, 12))
    
    # Grafo de precedências complexo
    # Estrutura diamante:
    #        0
    #      / | \
    #     1  2  3
    #     |  |  |
    #     4  5  6
    #      \ | /
    #        7
    #      / | \
    #     8  9  10
    #      \ | /
    #        11
    
    precedences = [
        # Primeira divisão
        (0, 1), (0, 2), (0, 3),
        # Caminhos paralelos
        (1, 4), (2, 5), (3, 6),
        # Convergência
        (4, 7), (5, 7), (6, 7),
        # Segunda divisão
        (7, 8), (7, 9), (7, 10),
        # Convergência final
        (8, 11), (9, 11), (10, 11)
    ]
    
    for i, j in precedences:
        instance.add_precedence(i, j)
    
    # Visualizar grafo
    visualize_precedence_graph(instance)
    
    # Resolver
    print("\n[EXECUTANDO ALGORITMO...]")
    rko = RKO_BRKGA(instance, population_size=100)
    solution, _ = rko.solve(brkga_generations=80, verbose=False)
    
    # Visualizar solução
    visualize_solution(solution, instance)
    
    return solution, instance


def exemplo_4_comparacao_configuracoes():
    """
    Exemplo 4: Comparação de diferentes configurações do algoritmo
    
    Demonstra o impacto dos parâmetros na qualidade da solução
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: COMPARAÇÃO DE CONFIGURAÇÕES")
    print("=" * 80)
    
    # Criar instância de teste
    instance = ALWABPInstance(n_tasks=10, n_workers=4, n_stations=4)
    np.random.seed(123)
    instance.execution_times = np.random.uniform(4, 9, (4, 10))
    
    for i in range(9):
        if i % 3 != 2:
            instance.add_precedence(i, i + 1)
    
    print("\nTestando diferentes configurações na mesma instância...")
    
    # Configuração 1: População pequena
    print("\n[CONFIG 1: População pequena (50)]")
    rko1 = RKO_BRKGA(instance, population_size=50)
    sol1, time1 = rko1.solve(brkga_generations=50, verbose=False)
    print(f"Resultado: Ciclo={sol1.cycle_time:.2f}, Tempo={time1:.2f}s")
    
    # Configuração 2: População grande
    print("\n[CONFIG 2: População grande (150)]")
    rko2 = RKO_BRKGA(instance, population_size=150)
    sol2, time2 = rko2.solve(brkga_generations=50, verbose=False)
    print(f"Resultado: Ciclo={sol2.cycle_time:.2f}, Tempo={time2:.2f}s")
    
    # Configuração 3: Busca local intensiva
    print("\n[CONFIG 3: Busca local intensiva]")
    rko3 = RKO_BRKGA(instance, population_size=100)
    sol3, time3 = rko3.solve(
        brkga_generations=50,
        local_search_freq=5,
        local_search_iterations=100,
        verbose=False
    )
    print(f"Resultado: Ciclo={sol3.cycle_time:.2f}, Tempo={time3:.2f}s")
    
    # Comparar soluções
    print("\n" + "-" * 80)
    print("COMPARAÇÕES PAR-A-PAR")
    print("-" * 80)
    
    compare_solutions(sol1, sol2, instance, "Config 1 (pop=50)", "Config 2 (pop=150)")
    compare_solutions(sol2, sol3, instance, "Config 2 (pop=150)", "Config 3 (BL intensiva)")


def exemplo_5_instancia_real():
    """
    Exemplo 5: Simulação de cenário realista
    
    Baseado em casos típicos da indústria
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 5: CENÁRIO REALISTA DA INDÚSTRIA")
    print("=" * 80)
    print("\nCenário: Linha de montagem de componentes automotivos")
    print("- 15 tarefas representando operações de montagem")
    print("- 5 trabalhadores com diferentes níveis de experiência")
    print("- 5 estações de trabalho")
    print("- Meta: Produzir uma peça a cada 25 minutos (tempo de ciclo)")
    
    # Criar instância
    instance = ALWABPInstance(n_tasks=15, n_workers=5, n_stations=5)
    
    # Definir tempos baseados em experiência
    # Trabalhador 0: Veterano (tempos baixos)
    # Trabalhadores 1-2: Experientes (tempos médios)
    # Trabalhadores 3-4: Novatos (tempos altos)
    
    base_times = np.array([4, 5, 6, 3, 7, 5, 4, 6, 5, 7, 4, 6, 5, 4, 6])  # Tempos base
    
    instance.execution_times = np.array([
        base_times * 0.8,   # Veterano: 20% mais rápido
        base_times * 1.0,   # Experiente 1
        base_times * 1.0,   # Experiente 2
        base_times * 1.3,   # Novato 1: 30% mais lento
        base_times * 1.3,   # Novato 2: 30% mais lento
    ])
    
    # Precedências realistas (montagem sequencial com algumas paralelas)
    precedences = [
        (0, 1), (0, 2),         # Preparação inicial bifurca
        (1, 3), (2, 3),         # Convergem
        (3, 4), (3, 5),         # Bifurca novamente
        (4, 6), (5, 7),         # Caminhos paralelos
        (6, 8), (7, 8),         # Convergem
        (8, 9), (9, 10),        # Sequência
        (10, 11), (10, 12),     # Bifurca
        (11, 13), (12, 13),     # Convergem
        (13, 14)                # Final
    ]
    
    for i, j in precedences:
        instance.add_precedence(i, j)
    
    # Algumas incompatibilidades (tarefas que requerem treinamento específico)
    instance.set_incompatible_task(3, 4)   # Novato 1 não pode fazer tarefa 4
    instance.set_incompatible_task(4, 7)   # Novato 2 não pode fazer tarefa 7
    instance.set_incompatible_task(3, 11)  # Novato 1 não pode fazer tarefa 11
    
    # Visualizar configuração
    visualize_worker_capabilities(instance)
    
    # Resolver com configuração robusta
    print("\n[EXECUTANDO ALGORITMO COM CONFIGURAÇÃO ROBUSTA...]")
    rko = RKO_BRKGA(
        instance,
        population_size=150,
        elite_size=0.25,      # Mais elite para explorar boas soluções
        mutant_size=0.10,
        elite_bias=0.75       # Maior viés para elite
    )
    
    solution, exec_time = rko.solve(
        brkga_generations=100,
        local_search_freq=8,
        local_search_iterations=60,
        verbose=True
    )
    
    # Análise da solução
    visualize_solution(solution, instance)
    
    print("\n" + "=" * 80)
    print("ANÁLISE DO RESULTADO")
    print("=" * 80)
    
    meta_ciclo = 25.0
    if solution.cycle_time <= meta_ciclo:
        print(f"✓ META ATINGIDA! Tempo de ciclo: {solution.cycle_time:.2f} min")
        print(f"  Margem de segurança: {meta_ciclo - solution.cycle_time:.2f} min")
    else:
        print(f"✗ Meta não atingida. Tempo de ciclo: {solution.cycle_time:.2f} min")
        print(f"  Excesso: {solution.cycle_time - meta_ciclo:.2f} min")
        print(f"  Sugestão: Adicionar mais uma estação ou redistribuir tarefas")
    
    print("\nRecomendações operacionais:")
    gargalo = np.argmax(solution.station_times)
    print(f"- Estação gargalo: Estação {gargalo}")
    print(f"- Monitorar trabalhador: Trabalhador {solution.worker_assignment[gargalo]}")
    
    return solution, instance


def main():
    """Menu principal para executar os exemplos"""
    print("=" * 80)
    print("EXEMPLOS DE USO - RKO-BRKGA PARA ALWABP")
    print("=" * 80)
    
    exemplos = {
        '1': ('Linha de produção simples', exemplo_1_linha_simples),
        '2': ('Trabalhadores especializados', exemplo_2_trabalhadores_especializados),
        '3': ('Grafo de precedências complexo', exemplo_3_grafo_complexo),
        '4': ('Comparação de configurações', exemplo_4_comparacao_configuracoes),
        '5': ('Cenário realista da indústria', exemplo_5_instancia_real),
        '6': ('Executar todos os exemplos', None)
    }
    
    print("\nExemplos disponíveis:")
    for key, (desc, _) in exemplos.items():
        print(f"{key} - {desc}")
    
    escolha = input("\nEscolha um exemplo (1-6): ").strip()
    
    if escolha == '6':
        # Executar todos
        for key in ['1', '2', '3', '4', '5']:
            input(f"\n\nPressione ENTER para executar exemplo {key}...")
            exemplos[key][1]()
    elif escolha in exemplos and escolha != '6':
        exemplos[escolha][1]()
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()
