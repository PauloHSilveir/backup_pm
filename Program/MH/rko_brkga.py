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
from Program.MH.elite_pool import ElitePool


class RKO_BRKGA:
    """
    Classe principal que implementa RKO com BRKGA + Busca Local
    """
    
    def __init__(self, 
                 instance: ALWABPInstance,
                 population_size: int = 100,
                 elite_size: float = 0.2,
                 mutant_size: float = 0.1,
                 elite_bias: float = 0.7,
                 elite_pool_size: int = 10):
        """
        Inicializa o algoritmo RKO-BRKGA
        
        Args:
            instance: instância do problema ALWABP
            population_size: tamanho da população do BRKGA
            elite_size: proporção de indivíduos elite
            mutant_size: proporção de indivíduos mutantes
            elite_bias: viés para herança de genes do elite
            elite_pool_size: tamanho do pool de soluções elite globais
        """
        self.instance = instance
        self.decoder = RandomKeyDecoder(instance)
        self.local_search = LocalSearch(instance)
        self.elite_pool = ElitePool(max_size=elite_pool_size, min_distance=0.15)
        
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
        self.execution_time = 0
        self.generations_without_improvement = 0
        self.last_best_fitness = np.inf
        
    def solve(self, 
              brkga_generations: int = 100,
              local_search_freq: int = 10,
              local_search_iterations: int = 50,
              restart_threshold: int = 50,
              verbose: bool = True) -> Tuple[ALWABPSolution, float]:
        """
        Executa o algoritmo RKO-BRKGA completo
        
        Args:
            brkga_generations: número de gerações do BRKGA
            local_search_freq: frequência (em gerações) para aplicar busca local
            local_search_iterations: iterações da busca local
            restart_threshold: gerações sem melhoria para acionar restart
            verbose: se True, imprime progresso detalhado
            
        Returns:
            Tupla (melhor solução, tempo de execução)
        """
        start_time = time.time()
        
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
        
        # Adicionar melhor inicial ao pool de elite
        self.elite_pool.add(self.best_solution)
        
        if verbose:
            print(f"  População inicial criada")
            print(f"  Melhor solução inicial: {self.best_cycle_time:.2f}")
            print(f"  Factível: {self.best_solution.is_feasible()}")
            print(f"  Pool de elite: {self.elite_pool}")
        
        if verbose:
            print(f"Melhor solução inicial: {self.best_cycle_time:.2f}")
            print(f"Factível: {self.best_solution.is_feasible()}")
        
        # Fase 2: Evolução do BRKGA com busca local periódica
        if verbose:
            print(f"\n[FASE 2] Executando BRKGA com busca local a cada {local_search_freq} gerações...")
        
        for generation in range(brkga_generations):
            # Evoluir uma geração
            self.brkga.evolve(generations=1, verbose=False)
            
            # Aplicar busca local periodicamente
            if (generation + 1) % local_search_freq == 0:
                current_best = self.brkga.get_best_solution()
                
                if verbose:
                    print(f"\n  Geração {generation + 1}: Aplicando busca local...")
                    print(f"    Antes da BL: {current_best.cycle_time:.2f}")
                
                # Aplicar busca local
                improved_solution = self.local_search.improve(
                    current_best, 
                    max_iterations=local_search_iterations
                )
                
                if verbose:
                    print(f"    Depois da BL: {improved_solution.cycle_time:.2f}")
                    improvement = current_best.cycle_time - improved_solution.cycle_time
                    print(f"    Melhoria: {improvement:.2f}")
                
                # Atualizar melhor solução global
                if improved_solution.cycle_time < self.best_cycle_time:
                    self.best_solution = improved_solution
                    self.best_cycle_time = improved_solution.cycle_time
                
                # Adicionar ao pool de elite
                added_to_pool = self.elite_pool.add(improved_solution)
                if verbose and added_to_pool:
                    print(f"    Adicionada ao pool de elite: {self.elite_pool}")
                
                # Inserir solução melhorada na população
                # Codificar solução de volta para cromossomo
                improved_chromosome = self.decoder.encode(improved_solution)
                
                # Substituir o pior indivíduo da população
                worst_idx = np.argmax(self.brkga.fitness)
                self.brkga.population[worst_idx] = improved_chromosome
                self.brkga.fitness[worst_idx] = improved_solution.cycle_time
                
                if verbose:
                    print(f"    Solução inserida na população (substituiu pior: {self.brkga.fitness[worst_idx]:.2f})")

            
            # Atualizar melhor solução global
            current_best_fitness = self.brkga.get_best_fitness()
            if current_best_fitness < self.best_cycle_time:
                self.best_solution = self.brkga.get_best_solution()
                self.best_cycle_time = current_best_fitness
                self.elite_pool.add(self.best_solution)
                self.generations_without_improvement = 0
                self.last_best_fitness = self.best_cycle_time
            else:
                self.generations_without_improvement += 1
            
            # Restart inteligente quando convergir
            if self.generations_without_improvement >= restart_threshold and not self.elite_pool.is_empty():
                if verbose:
                    print(f"\n  *** RESTART em geração {generation + 1} ***")
                    print(f"      Sem melhoria por {self.generations_without_improvement} gerações")
                    print(f"      Reiniciando população com elites do pool...")
                
                self._restart_with_elite_pool(verbose)
                self.generations_without_improvement = 0
            
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
            print("\n" + "=" * 70)
            print("RESULTADOS FINAIS")
            print("=" * 70)
            print(f"Melhor tempo de ciclo: {self.best_cycle_time:.2f}")
            print(f"Solução factível: {self.best_solution.is_feasible()}")
            print(f"Pool de elite final: {self.elite_pool}")
            print(f"Tempo de execução: {self.execution_time:.2f} segundos")
            print("=" * 70)
        
        return self.best_solution, self.execution_time
    
    def _restart_with_elite_pool(self, verbose: bool = False):
        """
        Reinicia população usando soluções do pool de elite.
        Mantém elite atual e preenche resto com perturbações das elites do pool.
        """
        # Obter top elites do pool
        top_elites = self.elite_pool.get_top_k(min(5, self.elite_pool.size()))
        
        if verbose:
            print(f"      Usando {len(top_elites)} elites do pool")
        
        # Criar nova população
        new_population = np.zeros_like(self.brkga.population)
        new_fitness = np.zeros_like(self.brkga.fitness)
        
        idx = 0
        
        # Preencher com elites do pool (codificadas + perturbadas)
        for elite_sol in top_elites:
            if idx >= self.brkga.population_size:
                break
            
            # Adicionar elite original
            chromosome = self.decoder.encode(elite_sol)
            new_population[idx] = chromosome
            new_fitness[idx] = elite_sol.cycle_time
            idx += 1
            
            # Adicionar versões perturbadas da elite (diversificação)
            n_perturbations = min(3, (self.brkga.population_size - idx) // len(top_elites))
            for _ in range(n_perturbations):
                if idx >= self.brkga.population_size:
                    break
                    
                # Perturbar cromossomo (20% dos genes)
                perturbed = chromosome.copy()
                n_genes_perturb = int(0.2 * len(chromosome))
                perturb_idx = np.random.choice(len(chromosome), n_genes_perturb, replace=False)
                perturbed[perturb_idx] = np.random.rand(n_genes_perturb)
                
                # Decodificar e avaliar
                perturbed_sol = self.decoder.decode(perturbed)
                new_population[idx] = perturbed
                new_fitness[idx] = perturbed_sol.cycle_time
                idx += 1
        
        # Preencher restante com soluções aleatórias
        while idx < self.brkga.population_size:
            new_population[idx] = np.random.rand(self.brkga.chromosome_size)
            sol = self.decoder.decode(new_population[idx])
            new_fitness[idx] = sol.cycle_time
            idx += 1
        
        # Substituir população
        self.brkga.population = new_population
        self.brkga.fitness = new_fitness
        
        if verbose:
            best_after = np.min(new_fitness)
            avg_after = np.mean(new_fitness[new_fitness < np.inf])
            print(f"      População reiniciada: melhor={best_after:.2f}, média={avg_after:.2f}")
    
    def get_best_solution(self) -> ALWABPSolution:
        """Retorna a melhor solução encontrada"""
        return self.best_solution
    
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
