"""
Script de testes e experimentos para o RKO-BRKGA

Este script permite testar diferentes configurações e comparar resultados
"""

import numpy as np
import time
from alwabp_instance import ALWABPInstance
from rko_brkga import RKO_BRKGA
from typing import List, Dict


def run_experiment(instance: ALWABPInstance, 
                   config: Dict,
                   n_runs: int = 5) -> Dict:
    """
    Executa múltiplas rodadas do algoritmo e retorna estatísticas
    
    Args:
        instance: Instância do problema
        config: Configuração dos parâmetros
        n_runs: Número de execuções
        
    Returns:
        Dicionário com estatísticas
    """
    results = {
        'cycle_times': [],
        'execution_times': [],
        'feasible': []
    }
    
    print(f"\nExecutando {n_runs} rodadas com configuração:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    for run in range(n_runs):
        print(f"\n  Rodada {run + 1}/{n_runs}...", end=" ")
        
        rko = RKO_BRKGA(
            instance=instance,
            population_size=config['population_size'],
            elite_size=config['elite_size'],
            mutant_size=config['mutant_size'],
            elite_bias=config['elite_bias']
        )
        
        solution, exec_time = rko.solve(
            brkga_generations=config['generations'],
            local_search_freq=config['ls_freq'],
            local_search_iterations=config['ls_iterations'],
            verbose=False
        )
        
        results['cycle_times'].append(solution.cycle_time)
        results['execution_times'].append(exec_time)
        results['feasible'].append(solution.is_feasible())
        
        print(f"Ciclo: {solution.cycle_time:.2f}, Tempo: {exec_time:.2f}s")
    
    # Calcular estatísticas
    results['mean_cycle_time'] = np.mean(results['cycle_times'])
    results['std_cycle_time'] = np.std(results['cycle_times'])
    results['best_cycle_time'] = np.min(results['cycle_times'])
    results['worst_cycle_time'] = np.max(results['cycle_times'])
    results['mean_exec_time'] = np.mean(results['execution_times'])
    results['all_feasible'] = all(results['feasible'])
    
    return results


def print_experiment_results(results: Dict):
    """Imprime resultados de um experimento"""
    print("\n" + "=" * 70)
    print("ESTATÍSTICAS DO EXPERIMENTO")
    print("=" * 70)
    print(f"Tempo de Ciclo:")
    print(f"  Melhor:  {results['best_cycle_time']:.2f}")
    print(f"  Pior:    {results['worst_cycle_time']:.2f}")
    print(f"  Média:   {results['mean_cycle_time']:.2f}")
    print(f"  Desvio:  {results['std_cycle_time']:.2f}")
    print(f"\nTempo de Execução Médio: {results['mean_exec_time']:.2f}s")
    print(f"Todas soluções factíveis: {results['all_feasible']}")
    print("=" * 70)


def compare_configurations():
    """Compara diferentes configurações do algoritmo"""
    print("=" * 70)
    print("COMPARAÇÃO DE CONFIGURAÇÕES")
    print("=" * 70)
    
    # Criar instância de teste
    np.random.seed(42)
    instance = ALWABPInstance(n_tasks=12, n_workers=4, n_stations=4)
    instance.execution_times = np.random.uniform(3, 10, (4, 12))
    
    # Adicionar precedências
    for i in range(11):
        if i % 3 != 2:
            instance.add_precedence(i, i + 1)
    
    # Configurações a testar
    configurations = [
        {
            'name': 'Configuração 1: Padrão',
            'population_size': 100,
            'elite_size': 0.2,
            'mutant_size': 0.1,
            'elite_bias': 0.7,
            'generations': 50,
            'ls_freq': 10,
            'ls_iterations': 30
        },
        {
            'name': 'Configuração 2: População Maior',
            'population_size': 150,
            'elite_size': 0.2,
            'mutant_size': 0.1,
            'elite_bias': 0.7,
            'generations': 50,
            'ls_freq': 10,
            'ls_iterations': 30
        },
        {
            'name': 'Configuração 3: Mais Elite',
            'population_size': 100,
            'elite_size': 0.3,
            'mutant_size': 0.1,
            'elite_bias': 0.7,
            'generations': 50,
            'ls_freq': 10,
            'ls_iterations': 30
        },
        {
            'name': 'Configuração 4: Busca Local Intensiva',
            'population_size': 100,
            'elite_size': 0.2,
            'mutant_size': 0.1,
            'elite_bias': 0.7,
            'generations': 50,
            'ls_freq': 5,
            'ls_iterations': 50
        }
    ]
    
    all_results = []
    
    for config in configurations:
        print("\n" + "=" * 70)
        print(config['name'])
        name = config.pop('name')
        results = run_experiment(instance, config, n_runs=3)
        results['name'] = name
        all_results.append(results)
        print_experiment_results(results)
    
    # Comparação final
    print("\n" + "=" * 70)
    print("COMPARAÇÃO FINAL")
    print("=" * 70)
    print(f"{'Configuração':<35} {'Melhor':<10} {'Média':<10} {'Tempo(s)':<10}")
    print("-" * 70)
    
    for result in all_results:
        print(f"{result['name']:<35} "
              f"{result['best_cycle_time']:<10.2f} "
              f"{result['mean_cycle_time']:<10.2f} "
              f"{result['mean_exec_time']:<10.2f}")
    
    print("=" * 70)


def test_scalability():
    """Testa escalabilidade com instâncias de diferentes tamanhos"""
    print("=" * 70)
    print("TESTE DE ESCALABILIDADE")
    print("=" * 70)
    
    sizes = [
        (8, 3, 3),    # Pequena
        (12, 4, 4),   # Média
        (20, 5, 5),   # Grande
    ]
    
    config = {
        'population_size': 100,
        'elite_size': 0.2,
        'mutant_size': 0.1,
        'elite_bias': 0.7,
        'generations': 50,
        'ls_freq': 10,
        'ls_iterations': 30
    }
    
    for n_tasks, n_workers, n_stations in sizes:
        print(f"\n{'=' * 70}")
        print(f"Instância: {n_tasks} tarefas, {n_workers} trabalhadores, {n_stations} estações")
        print("=" * 70)
        
        # Criar instância
        np.random.seed(42)
        instance = ALWABPInstance(n_tasks, n_workers, n_stations)
        instance.execution_times = np.random.uniform(3, 10, (n_workers, n_tasks))
        
        # Adicionar precedências
        for i in range(n_tasks - 1):
            if i % 3 != 2:
                instance.add_precedence(i, i + 1)
        
        # Executar
        results = run_experiment(instance, config, n_runs=3)
        print_experiment_results(results)


def main():
    """Função principal do script de testes"""
    print("=" * 70)
    print("SCRIPT DE TESTES E EXPERIMENTOS - RKO-BRKGA")
    print("=" * 70)
    
    print("\nEscolha o tipo de teste:")
    print("1 - Comparar diferentes configurações")
    print("2 - Testar escalabilidade")
    print("3 - Executar ambos")
    
    choice = input("\nOpção (1, 2 ou 3): ").strip()
    
    if choice == "1":
        compare_configurations()
    elif choice == "2":
        test_scalability()
    elif choice == "3":
        compare_configurations()
        print("\n\n")
        test_scalability()
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()
