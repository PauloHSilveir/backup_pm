"""
Algoritmo RKO (Random Key Optimization) com BRKGA + Busca Local
para o problema ALWABP (Assembly Line Worker Assignment and Balancing Problem)

Este módulo implementa a abordagem híbrida principal que combina:
- BRKGA: algoritmo genético com chaves aleatórias viesadas
- Busca Local: refinamento das soluções encontradas
"""

import numpy as np
import sys
import os
import time
from typing import Tuple

# Adicionar diretório Problem ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Problem'))

from Program.Problem.alwabp_instance import ALWABPInstance
from Program.Problem.alwabp_solution import ALWABPSolution
from Program.Problem.decoder import RandomKeyDecoder
from Program.MH.brkga import BRKGA
from Program.MH.local_search import LocalSearch


class RKO_BRKGA:
    """
    Classe principal que implementa RKO com BRKGA + Busca Local
    """
    
    def __init__(self, 
                 instance: ALWABPInstance,
                 population_size: int = 100,
                 elite_size: float = 0.25,
                 mutant_size: float = 0.15,
                 elite_bias: float = 0.75):
        """
        Inicializa o algoritmo RKO-BRKGA
        
        Args:
            instance: instância do problema ALWABP
            population_size: tamanho da população do BRKGA
            elite_size: proporção de indivíduos elite
            mutant_size: proporção de indivíduos mutantes
            elite_bias: viés para herança de genes do elite
        """
        self.instance = instance
        self.decoder = RandomKeyDecoder(instance)
        self.local_search = LocalSearch(instance)
        
        self.brkga = BRKGA(
            instance=instance,
            decoder=self.decoder,
            population_size=population_size,
            elite_size=elite_size,
            mutant_size=mutant_size,
            elite_bias=elite_bias
        )
        
        self.best_solution = None
        self.best_cycle_time = np.inf
        self.initial_solution = None
        self.initial_cycle_time = np.inf
        self.execution_time = 0
        self.optimal_value = None
        
    def solve(self, 
              brkga_generations: int = 100,
              local_search_freq: int = 10,
              local_search_iterations: int = 100,
              optimal_value: float = None,
              verbose: bool = True) -> Tuple[ALWABPSolution, float]:
        """
        Executa o algoritmo RKO-BRKGA completo
        
        Args:
            brkga_generations: número de gerações do BRKGA
            local_search_freq: frequência (em gerações) para aplicar busca local
            local_search_iterations: iterações da busca local
            optimal_value: valor da solução ótima (para cálculo de gap)
            verbose: se True, imprime progresso detalhado
            
        Returns:
            Tupla (melhor solução, tempo de execução)
        """
        start_time = time.time()
        
        # Armazenar valor ótimo se fornecido
        self.optimal_value = optimal_value
        
        if verbose:
            print("=" * 70)
            print("RKO-BRKGA para ALWABP")
            print("=" * 70)
            print(f"Instância: {self.instance.n_tasks} tarefas, "
                  f"{self.instance.n_workers} trabalhadores, "
                  f"{self.instance.n_stations} estações")
            print(f"População: {self.brkga.population_size}")
            print(f"Gerações: {brkga_generations}")
            print("=" * 70)
        
        # Fase 1: Inicializar população
        if verbose:
            print("\n[FASE 1] Inicializando população...")
        
        self.brkga.initialize_population()
        self.best_solution = self.brkga.get_best_solution()
        self.best_cycle_time = self.brkga.get_best_fitness()
        
        # Armazenar solução inicial (SI)
        self.initial_solution = self.best_solution
        self.initial_cycle_time = self.best_cycle_time
        
        if verbose:
            print(f"  População inicial criada")
            print(f"  Melhor solução inicial: {self.best_cycle_time:.2f}")
            print(f"  Factível: {self.best_solution.is_feasible()}")
        
        # Fase 2: Evolução do BRKGA com busca local periódica
        if verbose:
            print(f"\n[FASE 2] Executando BRKGA com busca local a cada {local_search_freq} gerações...")
        
        for generation in range(brkga_generations):
            # Evoluir uma geração
            self.brkga.evolve(generations=1, verbose=False)
            
            # Aplicar busca local periodicamente
            if (generation + 1) % local_search_freq == 0:
                if verbose:
                    print(f"\n  Geração {generation + 1}: Aplicando busca local...")
                
                # Aplicar BL nas TOP-3 soluções elite para explorar mais
                sorted_idx = np.argsort(self.brkga.fitness)
                top_k = min(3, self.brkga.elite_count)
                
                best_improvement = 0
                best_improved = None
                
                for k in range(top_k):
                    idx = sorted_idx[k]
                    current_solution = self.decoder.decode(self.brkga.population[idx])
                    current_fitness = self.brkga.fitness[idx]
                    
                    # Aplicar busca local
                    improved_solution = self.local_search.improve(
                        current_solution, 
                        max_iterations=local_search_iterations
                    )
                    
                    improvement = current_fitness - improved_solution.cycle_time
                    
                    if k == 0 and verbose:
                        print(f"    Melhor global: {current_fitness:.2f} → {improved_solution.cycle_time:.2f} (melhoria: {improvement:.2f})")
                    
                    # Rastrear melhor melhoria
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_improved = improved_solution
                    
                    # Atualizar melhor global se encontrou algo melhor
                    if improved_solution.cycle_time < self.best_cycle_time:
                        self.best_solution = improved_solution
                        self.best_cycle_time = improved_solution.cycle_time
                    
                    # Inserir solução melhorada na população (substituindo pior)
                    if improvement > 0:
                        improved_chromosome = self.decoder.encode(improved_solution)
                        worst_idx = np.argmax(self.brkga.fitness)
                        self.brkga.population[worst_idx] = improved_chromosome
                        self.brkga.fitness[worst_idx] = improved_solution.cycle_time
                
                if verbose and best_improvement > 0:
                    print(f"    Melhor melhoria encontrada: {best_improvement:.2f}")
                elif verbose:
                    print(f"    Nenhuma melhoria encontrada nas top-{top_k} soluções")

            
            # Atualizar melhor solução global
            current_best_fitness = self.brkga.get_best_fitness()
            if current_best_fitness < self.best_cycle_time:
                self.best_solution = self.brkga.get_best_solution()
                self.best_cycle_time = current_best_fitness
            
            # Progresso a cada 20 gerações
            if verbose and (generation + 1) % 20 == 0:
                avg_fitness = np.mean(self.brkga.fitness)
                print(f"\n  Geração {generation + 1}:")
                print(f"    Melhor global: {self.best_cycle_time:.2f}")
                print(f"    Melhor população: {current_best_fitness:.2f}")
                print(f"    Média população: {avg_fitness:.2f}")
        
        # Fase 3: Busca local final intensiva
        if verbose:
            print(f"\n[FASE 3] Aplicando busca local final intensiva...")
            print(f"  Antes da BL final: {self.best_cycle_time:.2f}")
        
        final_solution = self.local_search.improve(
            self.best_solution,
            max_iterations=local_search_iterations * 2
        )
        
        if final_solution.cycle_time < self.best_cycle_time:
            self.best_solution = final_solution
            self.best_cycle_time = final_solution.cycle_time
        
        self.execution_time = time.time() - start_time
        
        # Resultados finais
        if verbose:
            print(f"  Depois da BL final: {self.best_cycle_time:.2f}")
            self._print_computational_results(optimal_value=self.optimal_value)
        
        return self.best_solution, self.execution_time
    
    def get_best_solution(self) -> ALWABPSolution:
        """Retorna a melhor solução encontrada"""
        return self.best_solution
    
    def _print_computational_results(self, optimal_value=None):
        """
        Imprime tabela de resultados computacionais conforme especificação.
        
        Args:
            optimal_value: valor da solução ótima (se disponível)
        """
        print("\n" + "=" * 90)
        print("RESULTADOS COMPUTACIONAIS")
        print("=" * 90)
        
        # Valores
        si = self.initial_cycle_time
        sf = self.best_cycle_time
        
        # Desvio SI-SF: 100 × (SI - SF) / SI
        desvio_si_sf = 100 * (si - sf) / si if si > 0 else 0.0
        
        # Desvio SF-Ótimo: 100 × (SF - Ótimo) / Ótimo
        desvio_otimo = None
        if optimal_value is not None and optimal_value > 0:
            desvio_otimo = 100 * (sf - optimal_value) / optimal_value
        
        # Cabeçalho da tabela
        print(f"\n{'Métrica':<40} {'Valor':>15}")
        print("-" * 90)
        
        # Dados
        print(f"{'Solução Inicial (SI)':<40} {si:>15.2f}")
        print(f"{'Solução Final (SF)':<40} {sf:>15.2f}")
        print(f"{'Desvio SI-SF (%)':<40} {desvio_si_sf:>15.2f}")
        
        if desvio_otimo is not None:
            print(f"{'Desvio SF-Ótimo (%)':<40} {desvio_otimo:>15.2f}")
        else:
            print(f"{'Desvio SF-Ótimo (%)':<40} {'N/A':>15}")
        
        print(f"{'Tempo Computacional (s)':<40} {self.execution_time:>15.2f}")
        print(f"{'Solução Factível':<40} {str(self.best_solution.is_feasible()):>15}")
        
        print("=" * 90)
        print(f"\nFórmula SI-SF: 100 × ({si:.2f} - {sf:.2f}) / {si:.2f} = {desvio_si_sf:.2f}%")
        if desvio_otimo is not None:
            print(f"Fórmula SF-Ótimo: 100 × ({sf:.2f} - {optimal_value:.2f}) / {optimal_value:.2f} = {desvio_otimo:.2f}%")
        print("=" * 90)
    
    def print_solution_details(self):
        """Imprime detalhes da melhor solução"""
        if self.best_solution is None:
            print("Nenhuma solução disponível. Execute solve() primeiro.")
            return
        
        print("\n" + "=" * 70)
        print("DETALHES DA SOLUÇÃO")
        print("=" * 70)
        
        print("\nAtribuição de trabalhadores às estações:")
        for station in range(self.instance.n_stations):
            worker = self.best_solution.worker_assignment[station]
            time = self.best_solution.station_times[station]
            print(f"  Estação {station}: Trabalhador {worker} (tempo: {time:.2f})")
        
        print("\nAtribuição de tarefas às estações:")
        for station in range(self.instance.n_stations):
            tasks = np.where(self.best_solution.task_assignment == station)[0]
            if len(tasks) > 0:
                print(f"  Estação {station}: Tarefas {list(tasks)}")
        
        print(f"\nTempo de ciclo (gargalo): {self.best_cycle_time:.2f}")
        print(f"Balanceamento: {self._calculate_balance():.2f}%")
        print("=" * 70)
    
    def _calculate_balance(self) -> float:
        """Calcula o balanceamento da linha (% de utilização média)"""
        if self.best_solution is None:
            return 0.0
        
        total_time = np.sum(self.best_solution.station_times)
        max_time = self.best_cycle_time * self.instance.n_stations
        
        if max_time == 0:
            return 0.0
        
        return (total_time / max_time) * 100
