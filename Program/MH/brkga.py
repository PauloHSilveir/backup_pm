"""
Módulo BRKGA (Biased Random-Key Genetic Algorithm) para o ALWABP
"""

import numpy as np
import sys
import os
from typing import List, Tuple
import random

# Adicionar diretório Problem ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Problem'))

from Program.Problem.alwabp_instance import ALWABPInstance
from Program.Problem.alwabp_solution import ALWABPSolution
from Program.Problem.decoder import RandomKeyDecoder


class BRKGA:
    """Implementa o algoritmo BRKGA para o ALWABP"""
    
    def __init__(
        self,
        instance: ALWABPInstance,
        decoder: RandomKeyDecoder,
        population_size: int = 100,
        elite_size: float = 0.2,
        mutant_size: float = 0.1,
        elite_bias: float = 0.7,
    ):
        """Inicializa o BRKGA.

        Pequenas salvaguardas garantem ao menos 1 elite e 1 mutante
        quando os parâmetros produzirem valores muito baixos, evitando
        populações degeneradas sem alterar o comportamento típico.
        """

        self.instance = instance
        self.decoder = decoder
        self.population_size = population_size
        self.elite_count = max(1, int(population_size * elite_size))
        self.mutant_count = max(1, int(population_size * mutant_size))
        self.elite_bias = elite_bias

        # Tamanho do cromossomo: n_tasks + n_workers
        self.chromosome_size = instance.n_tasks + instance.n_workers

        # População: matriz onde cada linha é um cromossomo
        self.population = np.zeros((population_size, self.chromosome_size))

        # Fitness de cada indivíduo (minimização: menor é melhor)
        self.fitness = np.full(population_size, np.inf)

        # Melhor solução encontrada
        self.best_chromosome = None
        self.best_solution = None
        self.best_fitness = np.inf
        
        # Controle de estagnação para reinicialização
        self.generations_without_improvement = 0
        self.stagnation_limit = 30  # Reinicializar após 30 gerações sem melhoria
        
    def initialize_population(self):
        """Inicializa a população com chaves aleatórias uniformes [0, 1]"""
        self.population = np.random.rand(self.population_size, self.chromosome_size)
        
        # Avaliar população inicial com estratégias diversificadas
        for i in range(self.population_size):
            # Distribuir estratégias uniformemente na população inicial
            strategy = i % 3
            solution = self.decoder.decode(self.population[i], strategy=strategy)
            
            # Verificar factibilidade
            if solution.is_feasible():
                self.fitness[i] = solution.cycle_time
            else:
                self.fitness[i] = np.inf
            
            if self.fitness[i] < self.best_fitness:
                self.best_fitness = self.fitness[i]
                self.best_chromosome = self.population[i].copy()
                self.best_solution = solution
    
    def evolve(self, generations: int = 100, verbose: bool = True) -> ALWABPSolution:
        """
        Executa o algoritmo evolutivo
        
        Args:
            generations: número de gerações
            verbose: se True, imprime progresso
            
        Returns:
            Melhor solução encontrada
        """
        for generation in range(generations):
            # Verificar estagnação e reinicializar parcialmente se necessário
            if self.generations_without_improvement >= self.stagnation_limit:
                if verbose:
                    print(f"  >>> Reinicialização parcial (estagnado por {self.stagnation_limit} gerações)")
                self._partial_restart()
                self.generations_without_improvement = 0
            
            # Classificar população por fitness
            sorted_indices = np.argsort(self.fitness)
            self.population = self.population[sorted_indices]
            self.fitness = self.fitness[sorted_indices]
            
            # Nova população
            new_population = np.zeros_like(self.population)
            
            # Elitismo: manter os melhores
            new_population[:self.elite_count] = self.population[:self.elite_count]
            
            # Gerar mutantes
            mutant_start = self.elite_count
            mutant_end = self.elite_count + self.mutant_count
            new_population[mutant_start:mutant_end] = np.random.rand(self.mutant_count, self.chromosome_size)
            
            # Gerar descendentes por crossover
            offspring_count = max(0, self.population_size - self.elite_count - self.mutant_count)
            for i in range(offspring_count):
                idx = self.elite_count + self.mutant_count + i
                new_population[idx] = self._crossover()
            
            # Atualizar população
            self.population = new_population
            
            # Avaliar nova população (exceto elite que já foi avaliada)
            for i in range(self.elite_count, self.population_size):
                # Escolher estratégia: adaptativa para mutantes, distribuída para outros
                if i < self.elite_count + self.mutant_count:
                    strategy = None  # Adaptativa
                else:
                    strategy = i % 3  # Distribuída
                
                solution = self.decoder.decode(self.population[i], strategy=strategy)
                
                # Verificar factibilidade e penalizar se necessário
                if solution.is_feasible():
                    self.fitness[i] = solution.cycle_time
                else:
                    # Penalização: fitness muito alto para soluções infactíveis
                    self.fitness[i] = np.inf
                
                if self.fitness[i] < self.best_fitness:
                    self.best_fitness = self.fitness[i]
                    self.best_chromosome = self.population[i].copy()
                    self.best_solution = solution
            
            if verbose and (generation + 1) % 10 == 0:
                avg_fitness = np.mean(self.fitness)
                print(f"Geração {generation + 1}: Melhor = {self.best_fitness:.2f}, Média = {avg_fitness:.2f}")
        
        return self.best_solution
    
    def _crossover(self) -> np.ndarray:
        """
        Realiza crossover biased entre um elite e um não-elite
        
        Returns:
            Cromossomo filho
        """
        # Selecionar elite aleatório
        elite_idx = random.randint(0, self.elite_count - 1)
        
        # Selecionar não-elite aleatório
        non_elite_idx = random.randint(self.elite_count, self.population_size - 1)
        
        # Crossover parametrizado
        offspring = np.zeros(self.chromosome_size)
        for gene in range(self.chromosome_size):
            if random.random() < self.elite_bias:
                offspring[gene] = self.population[elite_idx][gene]
            else:
                offspring[gene] = self.population[non_elite_idx][gene]
        
        return offspring
    
    def _partial_restart(self):
        """
        Reinicializa 40% da população (mantendo elite protegida)
        Útil para escapar de ótimos locais
        """
        # Quantidade a reinicializar (40% da população, excluindo elite)
        restart_start = self.elite_count
        restart_count = int(0.4 * self.population_size)
        restart_end = min(restart_start + restart_count, self.population_size)
        
        # Reinicializar com novos cromossomos aleatórios
        for i in range(restart_start, restart_end):
            self.population[i] = np.random.rand(self.chromosome_size)
            solution = self.decoder.decode(self.population[i])
            self.fitness[i] = solution.cycle_time if solution.is_feasible() else np.inf
        
        # Garantir que melhor global está na população (substitui pior se necessário)
        if self.best_chromosome is not None:
            worst_idx = np.argmax(self.fitness)
            if self.fitness[worst_idx] > self.best_fitness:
                self.population[worst_idx] = self.best_chromosome.copy()
                self.fitness[worst_idx] = self.best_fitness
    
    def get_best_solution(self) -> ALWABPSolution:
        """Retorna a melhor solução encontrada"""
        return self.best_solution
    
    def get_best_fitness(self) -> float:
        """Retorna o melhor fitness encontrado"""
        return self.best_fitness
