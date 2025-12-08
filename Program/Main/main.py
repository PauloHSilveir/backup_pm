"""Ponto de entrada do RKO-BRKGA para o ALWABP.

Lê instância via stdin, executa réplicas independentes e imprime o melhor
tempo de ciclo encontrado. Opcionalmente salva a melhor solução em JSON.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

# Adicionar diretórios ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Problem"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "MH"))

from Program.MH.rko_brkga import RKO_BRKGA
from Program.Problem.read_instance import read_instance_from_stdin


@dataclass
class RunConfig:
    """Configuração efetiva usada em uma execução."""

    seed: Optional[int]
    pop_size: int
    generations: int
    elite: float
    mutant: float
    elite_bias: float
    ls_freq: int
    ls_iters: int


def parse_arguments() -> argparse.Namespace:
    """Lê argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="RKO-BRKGA para ALWABP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python3 main.py solution.json < instancia.txt\n"
            "  python3 main.py solution.json --seed 42 --replicas 5 < instancia.txt\n"
            "  python3 main.py solution.json --pop-size 200 --generations 300 < instancia.txt"
        ),
    )

    parser.add_argument("output_file", nargs="?", default=None, help="Arquivo para salvar a melhor solução (JSON)")
    parser.add_argument("--seed", type=int, default=None, help="Semente do gerador aleatório")
    parser.add_argument("--replicas", type=int, default=1, help="Número de réplicas com sementes diferentes")
    parser.add_argument("--pop-size", type=int, default=None, help="Tamanho da população")
    parser.add_argument("--generations", type=int, default=None, help="Número de gerações BRKGA")
    parser.add_argument("--elite", type=float, default=0.2, help="Percentual de indivíduos elite (0.0-1.0)")
    parser.add_argument("--mutant", type=float, default=0.1, help="Percentual de mutantes (0.0-1.0)")
    parser.add_argument("--elite-bias", type=float, default=0.7, help="Viés de elite no crossover (0.5-1.0)")
    parser.add_argument("--ls-freq", type=int, default=None, help="Frequência de busca local (gerações)")
    parser.add_argument("--ls-iters", type=int, default=None, help="Iterações de busca local")
    parser.add_argument("--optimal", type=float, default=None, help="Valor da solução ótima (para calcular gap)")
    parser.add_argument("--verbose", action="store_true", help="Modo verboso")

    return parser.parse_args()


def get_default_params(n_tasks: int) -> Dict[str, int]:
    """Retorna parâmetros padrão baseados no tamanho da instância."""
    if n_tasks <= 10:
        return {"population_size": 50, "generations": 50, "ls_freq": 10, "ls_iters": 30}
    if n_tasks <= 20:
        return {"population_size": 100, "generations": 100, "ls_freq": 10, "ls_iters": 50}
    if n_tasks <= 40:
        return {"population_size": 100, "generations": 100, "ls_freq": 25, "ls_iters": 30}
    return {"population_size": 100, "generations": 100, "ls_freq": 25, "ls_iters": 30}


def _build_run_config(args: argparse.Namespace, defaults: Dict[str, int], seed: Optional[int]) -> RunConfig:
    """Mescla argumentos com padrões para uma execução."""
    return RunConfig(
        seed=seed,
        pop_size=args.pop_size or defaults["population_size"],
        generations=args.generations or defaults["generations"],
        elite=args.elite,
        mutant=args.mutant,
        elite_bias=args.elite_bias,
        ls_freq=args.ls_freq or defaults["ls_freq"],
        ls_iters=args.ls_iters or defaults["ls_iters"],
    )


def run_single_execution(instance, args: argparse.Namespace, defaults: Dict[str, int], seed: Optional[int]):
    """Executa uma única replicação do algoritmo."""
    config = _build_run_config(args, defaults, seed)
    if config.seed is not None:
        np.random.seed(config.seed)

    rko = RKO_BRKGA(
        instance=instance,
        population_size=config.pop_size,
        elite_size=config.elite,
        mutant_size=config.mutant,
        elite_bias=config.elite_bias,
    )

    solution, exec_time = rko.solve(
        brkga_generations=config.generations,
        local_search_freq=config.ls_freq,
        local_search_iterations=config.ls_iters,
        optimal_value=args.optimal,
        verbose=args.verbose and args.replicas == 1,  # Verbose apenas se for 1 réplica
    )

    # Retornar também SI e SF para estatísticas
    return solution, exec_time, config, rko.initial_cycle_time, rko.best_cycle_time


def save_solution(filename, solution, instance, params: RunConfig, stats):
    """Salva a solução em formato JSON."""
    solution_data = {
        "cycle_time": float(solution.cycle_time),
        "feasible": solution.is_feasible(),
        "task_assignment": solution.task_assignment.tolist(),
        "worker_assignment": solution.worker_assignment.tolist(),
        "station_times": solution.station_times.tolist(),
        "instance": {"n_tasks": instance.n_tasks, "n_workers": instance.n_workers, "n_stations": instance.n_stations},
        "parameters": params.__dict__,
        "statistics": stats,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(solution_data, f, indent=2)


def _print_consolidated_results(initial_times, final_times, exec_times, optimal_value, n_replicas):
    """Imprime tabela consolidada de resultados de múltiplas réplicas."""
    print("\n" + "=" * 100, file=sys.stderr)
    print("RESULTADOS COMPUTACIONAIS - CONSOLIDADO DE RÉPLICAS", file=sys.stderr)
    print("=" * 100, file=sys.stderr)
    
    # Calcular estatísticas
    si_values = np.array(initial_times)
    sf_values = np.array(final_times)
    time_values = np.array(exec_times)
    
    # Desvios SI-SF para cada réplica
    desvios_si_sf = 100 * (si_values - sf_values) / si_values
    
    # Desvios SF-Ótimo se disponível
    desvios_otimo = None
    if optimal_value is not None and optimal_value > 0:
        desvios_otimo = 100 * (sf_values - optimal_value) / optimal_value
    
    # Tabela por réplica
    print(f"\n{'Réplica':<10} {'SI':>10} {'SF':>10} {'SI-SF(%)':>12} {'SF-Ót(%)':>12} {'Tempo(s)':>10}", file=sys.stderr)
    print("-" * 100, file=sys.stderr)
    
    for i in range(n_replicas):
        desvio_ot_str = f"{desvios_otimo[i]:>12.2f}" if desvios_otimo is not None else f"{'N/A':>12}"
        print(f"{i+1:<10} {si_values[i]:>10.2f} {sf_values[i]:>10.2f} {desvios_si_sf[i]:>12.2f} "
              f"{desvio_ot_str} {time_values[i]:>10.2f}", file=sys.stderr)
    
    print("-" * 100, file=sys.stderr)
    
    # Estatísticas gerais
    print(f"\n{'Estatística':<30} {'SI':>12} {'SF':>12} {'SI-SF(%)':>12} {'SF-Ót(%)':>12} {'Tempo(s)':>12}", file=sys.stderr)
    print("-" * 100, file=sys.stderr)
    
    print(f"{'Melhor':<30} {np.min(si_values):>12.2f} {np.min(sf_values):>12.2f} "
          f"{np.max(desvios_si_sf):>12.2f} ", end="", file=sys.stderr)
    if desvios_otimo is not None:
        print(f"{np.min(desvios_otimo):>12.2f} ", end="", file=sys.stderr)
    else:
        print(f"{'N/A':>12} ", end="", file=sys.stderr)
    print(f"{np.min(time_values):>12.2f}", file=sys.stderr)
    
    print(f"{'Média':<30} {np.mean(si_values):>12.2f} {np.mean(sf_values):>12.2f} "
          f"{np.mean(desvios_si_sf):>12.2f} ", end="", file=sys.stderr)
    if desvios_otimo is not None:
        print(f"{np.mean(desvios_otimo):>12.2f} ", end="", file=sys.stderr)
    else:
        print(f"{'N/A':>12} ", end="", file=sys.stderr)
    print(f"{np.mean(time_values):>12.2f}", file=sys.stderr)
    
    print(f"{'Pior':<30} {np.max(si_values):>12.2f} {np.max(sf_values):>12.2f} "
          f"{np.min(desvios_si_sf):>12.2f} ", end="", file=sys.stderr)
    if desvios_otimo is not None:
        print(f"{np.max(desvios_otimo):>12.2f} ", end="", file=sys.stderr)
    else:
        print(f"{'N/A':>12} ", end="", file=sys.stderr)
    print(f"{np.max(time_values):>12.2f}", file=sys.stderr)
    
    print(f"{'Desvio Padrão':<30} {np.std(si_values):>12.2f} {np.std(sf_values):>12.2f} "
          f"{np.std(desvios_si_sf):>12.2f} ", end="", file=sys.stderr)
    if desvios_otimo is not None:
        print(f"{np.std(desvios_otimo):>12.2f} ", end="", file=sys.stderr)
    else:
        print(f"{'N/A':>12} ", end="", file=sys.stderr)
    print(f"{np.std(time_values):>12.2f}", file=sys.stderr)
    
    print("=" * 100, file=sys.stderr)
    print(f"\nFórmula SI-SF: 100 × (SI - SF) / SI", file=sys.stderr)
    if optimal_value is not None:
        print(f"Fórmula SF-Ótimo: 100 × (SF - {optimal_value:.2f}) / {optimal_value:.2f}", file=sys.stderr)
    print(f"Número de réplicas: {n_replicas}", file=sys.stderr)
    print("=" * 100, file=sys.stderr)


def main() -> None:
    args = parse_arguments()

    try:
        instance = read_instance_from_stdin()
    except Exception as exc:  # pragma: no cover - caminho de erro somente CLI
        print(f"Erro ao ler instância: {exc}", file=sys.stderr)
        sys.exit(1)

    defaults = get_default_params(instance.n_tasks)

    best_solution = None
    best_cycle_time = float("inf")
    cycle_times = []
    exec_times = []
    initial_times = []
    best_params: Optional[RunConfig] = None

    for replica in range(max(1, args.replicas)):
        seed = (args.seed + replica) if args.seed is not None else None

        if args.verbose and args.replicas > 1:
            print(f"Executando réplica {replica + 1}/{args.replicas} (seed={seed})...", end=" ", file=sys.stderr, flush=True)

        solution, exec_time, params, si, sf = run_single_execution(instance, args, defaults, seed)
        cycle_times.append(sf)
        exec_times.append(exec_time)
        initial_times.append(si)

        if args.verbose and args.replicas > 1:
            print(f"✓ SF={sf:.2f}", file=sys.stderr, flush=True)

        if solution.cycle_time < best_cycle_time:
            best_cycle_time = solution.cycle_time
            best_solution = solution
            best_params = params

    assert best_solution is not None, "Deve haver ao menos uma solução"  # segurança interna

    stats = {
        "replicas": args.replicas,
        "best_cycle_time": float(np.min(cycle_times)),
        "mean_cycle_time": float(np.mean(cycle_times)),
        "std_cycle_time": float(np.std(cycle_times)) if args.replicas > 1 else 0.0,
        "mean_exec_time": float(np.mean(exec_times)),
        "all_cycle_times": [float(x) for x in cycle_times],
    }

    print(f"{best_solution.cycle_time:.2f}")

    if args.output_file and best_params is not None:
        save_solution(args.output_file, best_solution, instance, best_params, stats)
        print(f"Solução salva em: {args.output_file}", file=sys.stderr)

    # Tabela consolidada de resultados para múltiplas réplicas
    if args.replicas > 1 and args.verbose:
        _print_consolidated_results(
            initial_times, cycle_times, exec_times, args.optimal, args.replicas
        )
    elif args.replicas > 1:
        print(f"\nEstatísticas ({args.replicas} réplicas):", file=sys.stderr)
        print(f"  Melhor: {stats['best_cycle_time']:.2f}", file=sys.stderr)
        print(f"  Média: {stats['mean_cycle_time']:.2f}", file=sys.stderr)
        print(f"  Desvio: {stats['std_cycle_time']:.2f}", file=sys.stderr)

    if args.replicas > 1:
        print(f"Tempo médio: {stats['mean_exec_time']:.2f}s", file=sys.stderr)
        print(f"Factível: {best_solution.is_feasible()}", file=sys.stderr)


if __name__ == "__main__":
    main()
