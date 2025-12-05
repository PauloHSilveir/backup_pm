"""
Módulo de visualização para soluções do ALWABP

Funções para criar visualizações em texto das soluções
"""

import numpy as np
from alwabp_solution import ALWABPSolution
from alwabp_instance import ALWABPInstance
from typing import List


def visualize_solution(solution: ALWABPSolution, instance: ALWABPInstance):
    """
    Cria uma visualização textual completa da solução
    
    Args:
        solution: Solução a visualizar
        instance: Instância do problema
    """
    print("\n" + "=" * 80)
    print("VISUALIZAÇÃO DA SOLUÇÃO")
    print("=" * 80)
    
    # Informações gerais
    print(f"\nTempo de Ciclo: {solution.cycle_time:.2f}")
    print(f"Solução Factível: {solution.is_feasible()}")
    
    # Visualizar linha de produção
    print("\n" + "-" * 80)
    print("LINHA DE PRODUÇÃO")
    print("-" * 80)
    
    for station in range(instance.n_stations):
        worker = solution.worker_assignment[station]
        tasks = np.where(solution.task_assignment == station)[0]
        station_time = solution.station_times[station]
        
        print(f"\nEstação {station} | Trabalhador {worker} | Tempo Total: {station_time:.2f}")
        print("  " + "-" * 76)
        
        if len(tasks) > 0:
            print(f"  Tarefas: {list(tasks)}")
            print("  Detalhes das tarefas:")
            
            for task in tasks:
                task_time = instance.execution_times[worker][task]
                print(f"    Tarefa {task}: {task_time:.2f} unidades de tempo")
        else:
            print("  (Sem tarefas atribuídas)")
        
        # Barra de carga
        bar_length = 60
        bar_fill = int((station_time / solution.cycle_time) * bar_length)
        bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
        percentage = (station_time / solution.cycle_time) * 100
        print(f"  Carga: [{bar}] {percentage:.1f}%")
    
    # Estatísticas
    print("\n" + "-" * 80)
    print("ESTATÍSTICAS")
    print("-" * 80)
    
    total_time = np.sum(solution.station_times)
    max_possible_time = solution.cycle_time * instance.n_stations
    balance = (total_time / max_possible_time) * 100 if max_possible_time > 0 else 0
    
    min_time = np.min(solution.station_times)
    max_time = np.max(solution.station_times)
    mean_time = np.mean(solution.station_times)
    
    print(f"Tempo mínimo por estação: {min_time:.2f}")
    print(f"Tempo máximo por estação: {max_time:.2f}")
    print(f"Tempo médio por estação:  {mean_time:.2f}")
    print(f"Balanceamento da linha:   {balance:.2f}%")
    print(f"Ociosidade média:         {100 - balance:.2f}%")
    
    print("=" * 80)


def visualize_precedence_graph(instance: ALWABPInstance):
    """
    Visualiza o grafo de precedências em formato textual
    
    Args:
        instance: Instância do problema
    """
    print("\n" + "=" * 80)
    print("GRAFO DE PRECEDÊNCIAS")
    print("=" * 80)
    
    if len(instance.precedences) == 0:
        print("\n(Sem relações de precedência)")
    else:
        print("\nRelações diretas (i → j significa que i precede j):")
        for i, j in sorted(instance.precedences):
            print(f"  Tarefa {i} → Tarefa {j}")
        
        # Mostrar níveis topológicos
        prec_matrix = instance.get_precedence_matrix()
        levels = _compute_topological_levels(prec_matrix, instance.n_tasks)
        
        print("\nNíveis topológicos:")
        for level, tasks in enumerate(levels):
            if tasks:
                print(f"  Nível {level}: {sorted(tasks)}")
    
    print("=" * 80)


def _compute_topological_levels(prec_matrix: np.ndarray, n_tasks: int) -> List[List[int]]:
    """
    Calcula os níveis topológicos das tarefas
    
    Args:
        prec_matrix: Matriz de precedências
        n_tasks: Número de tarefas
        
    Returns:
        Lista de listas, onde cada lista contém as tarefas de um nível
    """
    levels = []
    assigned = set()
    
    while len(assigned) < n_tasks:
        current_level = []
        
        for task in range(n_tasks):
            if task in assigned:
                continue
            
            # Verificar se todas as predecessoras foram atribuídas
            predecessors_done = True
            for pred in range(n_tasks):
                if prec_matrix[pred][task] == 1 and pred not in assigned:
                    predecessors_done = False
                    break
            
            if predecessors_done:
                current_level.append(task)
        
        if not current_level:
            break  # Evitar loop infinito
        
        levels.append(current_level)
        assigned.update(current_level)
    
    return levels


def visualize_worker_capabilities(instance: ALWABPInstance):
    """
    Visualiza as capacidades e restrições dos trabalhadores
    
    Args:
        instance: Instância do problema
    """
    print("\n" + "=" * 80)
    print("CAPACIDADES DOS TRABALHADORES")
    print("=" * 80)
    
    for worker in range(instance.n_workers):
        print(f"\nTrabalhador {worker}:")
        
        # Tarefas compatíveis
        compatible_tasks = [t for t in range(instance.n_tasks) 
                          if t not in instance.incompatible_tasks[worker]]
        incompatible_tasks = list(instance.incompatible_tasks[worker])
        
        print(f"  Tarefas compatíveis: {compatible_tasks}")
        if incompatible_tasks:
            print(f"  Tarefas INCOMPATÍVEIS: {incompatible_tasks}")
        
        # Tempos médios
        compatible_times = [instance.execution_times[worker][t] 
                          for t in compatible_tasks]
        if compatible_times:
            avg_time = np.mean(compatible_times)
            min_time = np.min(compatible_times)
            max_time = np.max(compatible_times)
            
            print(f"  Tempo médio: {avg_time:.2f}")
            print(f"  Tempo mínimo: {min_time:.2f}")
            print(f"  Tempo máximo: {max_time:.2f}")
    
    print("=" * 80)


def compare_solutions(solution1: ALWABPSolution, 
                     solution2: ALWABPSolution,
                     instance: ALWABPInstance,
                     label1: str = "Solução 1",
                     label2: str = "Solução 2"):
    """
    Compara duas soluções lado a lado
    
    Args:
        solution1: Primeira solução
        solution2: Segunda solução
        instance: Instância do problema
        label1: Rótulo da primeira solução
        label2: Rótulo da segunda solução
    """
    print("\n" + "=" * 80)
    print(f"COMPARAÇÃO: {label1} vs {label2}")
    print("=" * 80)
    
    print(f"\n{'Métrica':<30} {label1:<20} {label2:<20} {'Diferença':<15}")
    print("-" * 80)
    
    # Tempo de ciclo
    diff_cycle = solution2.cycle_time - solution1.cycle_time
    print(f"{'Tempo de Ciclo':<30} {solution1.cycle_time:<20.2f} {solution2.cycle_time:<20.2f} {diff_cycle:<15.2f}")
    
    # Balanceamento
    total1 = np.sum(solution1.station_times)
    max1 = solution1.cycle_time * instance.n_stations
    balance1 = (total1 / max1) * 100 if max1 > 0 else 0
    
    total2 = np.sum(solution2.station_times)
    max2 = solution2.cycle_time * instance.n_stations
    balance2 = (total2 / max2) * 100 if max2 > 0 else 0
    
    diff_balance = balance2 - balance1
    print(f"{'Balanceamento (%)':<30} {balance1:<20.2f} {balance2:<20.2f} {diff_balance:<15.2f}")
    
    # Desvio padrão dos tempos
    std1 = np.std(solution1.station_times)
    std2 = np.std(solution2.station_times)
    diff_std = std2 - std1
    print(f"{'Desvio Padrão':<30} {std1:<20.2f} {std2:<20.2f} {diff_std:<15.2f}")
    
    # Factibilidade
    feas1 = "Sim" if solution1.is_feasible() else "Não"
    feas2 = "Sim" if solution2.is_feasible() else "Não"
    print(f"{'Factível':<30} {feas1:<20} {feas2:<20}")
    
    print("=" * 80)
    
    # Determinar vencedor
    if solution1.cycle_time < solution2.cycle_time:
        print(f"\n{label1} é MELHOR (menor tempo de ciclo)")
    elif solution2.cycle_time < solution1.cycle_time:
        print(f"\n{label2} é MELHOR (menor tempo de ciclo)")
    else:
        print("\nAmbas as soluções têm o mesmo tempo de ciclo")
    
    print("=" * 80)


if __name__ == "__main__":
    # Teste das funções de visualização
    from main import create_simple_instance
    
    instance = create_simple_instance()
    
    visualize_precedence_graph(instance)
    visualize_worker_capabilities(instance)
