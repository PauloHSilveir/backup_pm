"""
Script principal para executar o algoritmo RKO-BRKGA no problema ALWABP

Exemplo de uso e testes
"""

import numpy as np
from alwabp_instance import ALWABPInstance
from rko_brkga import RKO_BRKGA


def create_simple_instance() -> ALWABPInstance:
    """
    Cria uma instância simples de teste do ALWABP
    
    Returns:
        Instância de teste
    """
    # Instância pequena: 8 tarefas, 4 trabalhadores, 4 estações
    n_tasks = 8
    n_workers = 4
    n_stations = 4
    
    instance = ALWABPInstance(n_tasks, n_workers, n_stations)
    
    # Definir tempos de execução (matriz workers x tasks)
    # Cada linha é um trabalhador, cada coluna é uma tarefa
    execution_times = np.array([
        [5, 7, 3, 6, 4, 8, 5, 7],   # Trabalhador 0
        [6, 5, 4, 7, 5, 6, 4, 8],   # Trabalhador 1
        [7, 8, 5, 5, 6, 7, 6, 6],   # Trabalhador 2
        [4, 6, 6, 8, 7, 5, 7, 5],   # Trabalhador 3
    ], dtype=float)
    
    instance.execution_times = execution_times
    
    # Definir precedências (i precede j)
    # Exemplo: 0 -> 1 -> 3 -> 5 -> 7
    #          0 -> 2 -> 4 -> 6
    precedences = [
        (0, 1), (1, 3), (3, 5), (5, 7),  # Cadeia 1
        (0, 2), (2, 4), (4, 6),          # Cadeia 2
    ]
    
    for i, j in precedences:
        instance.add_precedence(i, j)
    
    # Definir algumas incompatibilidades
    # Trabalhador 1 não pode executar tarefa 5
    instance.set_incompatible_task(1, 5)
    # Trabalhador 3 não pode executar tarefa 2
    instance.set_incompatible_task(3, 2)
    
    return instance


def create_medium_instance() -> ALWABPInstance:
    """
    Cria uma instância média de teste do ALWABP
    
    Returns:
        Instância de teste
    """
    n_tasks = 15
    n_workers = 5
    n_stations = 5
    
    instance = ALWABPInstance(n_tasks, n_workers, n_stations)
    
    # Gerar tempos aleatórios mas consistentes (seed fixo)
    np.random.seed(42)
    instance.execution_times = np.random.uniform(3, 10, (n_workers, n_tasks))
    
    # Criar precedências em cadeia e algumas paralelas
    precedences = []
    for i in range(n_tasks - 1):
        if i % 3 != 2:  # Criar algumas tarefas em paralelo
            precedences.append((i, i + 1))
    
    # Adicionar algumas dependências cruzadas
    precedences.extend([(0, 3), (2, 5), (5, 8), (8, 11)])
    
    for i, j in precedences:
        instance.add_precedence(i, j)
    
    # Adicionar algumas incompatibilidades aleatórias
    for w in range(n_workers):
        incompatible_count = np.random.randint(1, 3)
        incompatible_tasks = np.random.choice(n_tasks, incompatible_count, replace=False)
        for task in incompatible_tasks:
            instance.set_incompatible_task(w, int(task))
    
    return instance


def main():
    """Função principal para testar o algoritmo"""
    
    print("=" * 70)
    print("RKO-BRKGA PARA ALWABP")
    print("Assembly Line Worker Assignment and Balancing Problem")
    print("=" * 70)
    
    # Escolher tipo de instância
    print("\nEscolha o tipo de instância:")
    print("1 - Instância simples (8 tarefas, 4 trabalhadores)")
    print("2 - Instância média (15 tarefas, 5 trabalhadores)")
    
    choice = input("\nOpção (1 ou 2): ").strip()
    
    if choice == "1":
        instance = create_simple_instance()
    elif choice == "2":
        instance = create_medium_instance()
    else:
        print("Opção inválida. Usando instância simples.")
        instance = create_simple_instance()
    
    # Configurar parâmetros do algoritmo
    print("\n" + "=" * 70)
    print("CONFIGURAÇÃO DO ALGORITMO")
    print("=" * 70)
    
    # Usar valores padrão ou personalizar
    use_default = input("\nUsar parâmetros padrão? (s/n): ").strip().lower()
    
    if use_default == 's':
        population_size = 100
        brkga_generations = 100
        local_search_freq = 10
        local_search_iterations = 50
    else:
        population_size = int(input("Tamanho da população (padrão: 100): ") or "100")
        brkga_generations = int(input("Número de gerações (padrão: 100): ") or "100")
        local_search_freq = int(input("Frequência da busca local (padrão: 10): ") or "10")
        local_search_iterations = int(input("Iterações da busca local (padrão: 50): ") or "50")
    
    # Criar e executar o algoritmo
    rko = RKO_BRKGA(
        instance=instance,
        population_size=population_size,
        elite_size=0.2,
        mutant_size=0.1,
        elite_bias=0.7
    )
    
    # Resolver
    solution, exec_time = rko.solve(
        brkga_generations=brkga_generations,
        local_search_freq=local_search_freq,
        local_search_iterations=local_search_iterations,
        verbose=True
    )
    
    # Imprimir detalhes da solução
    rko.print_solution_details()
    
    # Salvar resultados
    save = input("\nSalvar resultados em arquivo? (s/n): ").strip().lower()
    if save == 's':
        filename = input("Nome do arquivo (sem extensão): ").strip()
        save_results(rko, filename)
        print(f"\nResultados salvos em {filename}.txt")


def save_results(rko: RKO_BRKGA, filename: str):
    """Salva os resultados em um arquivo de texto"""
    with open(f"{filename}.txt", 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("RESULTADOS RKO-BRKGA PARA ALWABP\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Instância:\n")
        f.write(f"  Tarefas: {rko.instance.n_tasks}\n")
        f.write(f"  Trabalhadores: {rko.instance.n_workers}\n")
        f.write(f"  Estações: {rko.instance.n_stations}\n\n")
        
        f.write(f"Resultado:\n")
        f.write(f"  Tempo de ciclo: {rko.best_cycle_time:.2f}\n")
        f.write(f"  Solução factível: {rko.best_solution.is_feasible()}\n")
        f.write(f"  Tempo de execução: {rko.execution_time:.2f} segundos\n")
        f.write(f"  Balanceamento: {rko._calculate_balance():.2f}%\n\n")
        
        f.write("Atribuição de trabalhadores:\n")
        for station in range(rko.instance.n_stations):
            worker = rko.best_solution.worker_assignment[station]
            time = rko.best_solution.station_times[station]
            f.write(f"  Estação {station}: Trabalhador {worker} (tempo: {time:.2f})\n")
        
        f.write("\nAtribuição de tarefas:\n")
        for station in range(rko.instance.n_stations):
            tasks = np.where(rko.best_solution.task_assignment == station)[0]
            if len(tasks) > 0:
                f.write(f"  Estação {station}: Tarefas {list(tasks)}\n")


if __name__ == "__main__":
    main()
