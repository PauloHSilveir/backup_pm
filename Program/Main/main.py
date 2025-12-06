"""
Script principal para executar o algoritmo RKO-BRKGA no problema ALWABP

Lê instância da entrada padrão (stdin) e executa o algoritmo
Saída: melhor solução encontrada na saída padrão (stdout)

Uso: python3 main.py [output_file] [options] < instancia.txt

Parâmetros opcionais:
    --seed SEED                 Semente do gerador aleatório (padrão: None)
    --replicas N                Número de réplicas (padrão: 1)
    --pop-size SIZE             Tamanho da população (padrão: auto)
    --generations GEN           Número de gerações (padrão: auto)
    --elite PERC                Percentual de elite (padrão: 0.2)
    --mutant PERC               Percentual de mutantes (padrão: 0.1)
    --elite-bias BIAS           Viés de elite no crossover (padrão: 0.7)
    --ls-freq FREQ              Frequência de busca local (padrão: auto)
    --ls-iters ITERS            Iterações de busca local (padrão: auto)
    --verbose                   Modo verboso
"""

import sys
import os
import argparse
import json
import numpy as np

# Adicionar diretórios ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Problem'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MH'))

from Program.Problem.read_instance import read_instance_from_stdin
from Program.MH.rko_brkga import RKO_BRKGA


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='RKO-BRKGA para ALWABP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 main.py solution.json < instancia.txt
  python3 main.py solution.json --seed 42 --replicas 5 < instancia.txt
  python3 main.py solution.json --pop-size 200 --generations 300 < instancia.txt
        """
    )
    
    parser.add_argument('output_file', nargs='?', default=None,
                        help='Arquivo para salvar a melhor solução (JSON)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Semente do gerador aleatório')
    parser.add_argument('--replicas', type=int, default=1,
                        help='Número de réplicas com sementes diferentes')
    parser.add_argument('--pop-size', type=int, default=None,
                        help='Tamanho da população')
    parser.add_argument('--generations', type=int, default=None,
                        help='Número de gerações BRKGA')
    parser.add_argument('--elite', type=float, default=0.2,
                        help='Percentual de indivíduos elite (0.0-1.0)')
    parser.add_argument('--mutant', type=float, default=0.1,
                        help='Percentual de mutantes (0.0-1.0)')
    parser.add_argument('--elite-bias', type=float, default=0.7,
                        help='Viés de elite no crossover (0.5-1.0)')
    parser.add_argument('--ls-freq', type=int, default=None,
                        help='Frequência de busca local (gerações)')
    parser.add_argument('--ls-iters', type=int, default=None,
                        help='Iterações de busca local')
    parser.add_argument('--verbose', action='store_true',
                        help='Modo verboso')
    
    return parser.parse_args()


def get_default_params(n_tasks):
    """Retorna parâmetros padrão baseados no tamanho da instância"""
    if n_tasks <= 10:
        return {
            'population_size': 50,
            'generations': 50,
            'ls_freq': 10,
            'ls_iters': 30
        }
    elif n_tasks <= 20:
        return {
            'population_size': 100,
            'generations': 100,
            'ls_freq': 10,
            'ls_iters': 50
        }
    elif n_tasks <= 40:
        return {
            'population_size': 100,
            'generations': 100,
            'ls_freq': 25,
            'ls_iters': 30
        }
    else:
        return {
            'population_size': 100,
            'generations': 100,
            'ls_freq': 25,
            'ls_iters': 30
        }


def run_single_execution(instance, args, defaults, seed=None):
    """Executa uma única replicação do algoritmo"""
    if seed is not None:
        np.random.seed(seed)
    
    # Usar parâmetros da linha de comando ou padrões
    pop_size = args.pop_size if args.pop_size else defaults['population_size']
    generations = args.generations if args.generations else defaults['generations']
    ls_freq = args.ls_freq if args.ls_freq else defaults['ls_freq']
    ls_iters = args.ls_iters if args.ls_iters else defaults['ls_iters']
    
    # Criar e executar o algoritmo
    rko = RKO_BRKGA(
        instance=instance,
        population_size=pop_size,
        elite_size=args.elite,
        mutant_size=args.mutant,
        elite_bias=args.elite_bias
    )
    
    solution, exec_time = rko.solve(
        brkga_generations=generations,
        local_search_freq=ls_freq,
        local_search_iterations=ls_iters,
        verbose=args.verbose
    )
    
    return solution, exec_time, {
        'seed': seed,
        'pop_size': pop_size,
        'generations': generations,
        'elite': args.elite,
        'mutant': args.mutant,
        'elite_bias': args.elite_bias,
        'ls_freq': ls_freq,
        'ls_iters': ls_iters
    }


def save_solution(filename, solution, instance, params, stats):
    """Salva a solução em formato JSON"""
    solution_data = {
        'cycle_time': float(solution.cycle_time),
        'feasible': solution.is_feasible(),
        'task_assignment': solution.task_assignment.tolist(),
        'worker_assignment': solution.worker_assignment.tolist(),
        'station_times': solution.station_times.tolist(),
        'instance': {
            'n_tasks': instance.n_tasks,
            'n_workers': instance.n_workers,
            'n_stations': instance.n_stations
        },
        'parameters': params,
        'statistics': stats
    }
    
    with open(filename, 'w') as f:
        json.dump(solution_data, f, indent=2)


def main():
    """Função principal"""
    args = parse_arguments()
    
    # Ler instância da entrada padrão
    try:
        instance = read_instance_from_stdin()
    except Exception as e:
        print(f"Erro ao ler instância: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Obter parâmetros padrão
    defaults = get_default_params(instance.n_tasks)
    
    # Executar réplicas
    best_solution = None
    best_cycle_time = float('inf')
    cycle_times = []
    exec_times = []
    
    for replica in range(args.replicas):
        # Determinar semente
        if args.seed is not None:
            seed = args.seed + replica
        else:
            seed = None
        
        if args.verbose:
            print(f"Réplica {replica + 1}/{args.replicas} (seed={seed})", file=sys.stderr)
        
        solution, exec_time, params = run_single_execution(instance, args, defaults, seed)
        
        cycle_times.append(solution.cycle_time)
        exec_times.append(exec_time)
        
        if solution.cycle_time < best_cycle_time:
            best_cycle_time = solution.cycle_time
            best_solution = solution
            best_params = params
    
    # Estatísticas
    stats = {
        'replicas': args.replicas,
        'best_cycle_time': float(np.min(cycle_times)),
        'mean_cycle_time': float(np.mean(cycle_times)),
        'std_cycle_time': float(np.std(cycle_times)) if args.replicas > 1 else 0.0,
        'mean_exec_time': float(np.mean(exec_times)),
        'all_cycle_times': [float(x) for x in cycle_times]
    }
    
    # Saída padrão: melhor tempo de ciclo
    print(f"{best_solution.cycle_time:.2f}")
    
    # Salvar solução em arquivo se especificado
    if args.output_file:
        save_solution(args.output_file, best_solution, instance, best_params, stats)
        print(f"Solução salva em: {args.output_file}", file=sys.stderr)
    
    # Informações adicionais no stderr
    if args.replicas > 1:
        print(f"\nEstatísticas ({args.replicas} réplicas):", file=sys.stderr)
        print(f"  Melhor: {stats['best_cycle_time']:.2f}", file=sys.stderr)
        print(f"  Média: {stats['mean_cycle_time']:.2f}", file=sys.stderr)
        print(f"  Desvio: {stats['std_cycle_time']:.2f}", file=sys.stderr)
    
    print(f"Tempo médio: {stats['mean_exec_time']:.2f}s", file=sys.stderr)
    print(f"Factível: {best_solution.is_feasible()}", file=sys.stderr)


if __name__ == "__main__":
    main()
