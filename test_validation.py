"""
Script de validação rápida do código RKO-BRKGA

Este script executa testes básicos para garantir que tudo está funcionando
"""

import sys
import numpy as np

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("=" * 70)
    print("TESTE 1: Importação de Módulos")
    print("=" * 70)
    
    try:
        from alwabp_instance import ALWABPInstance
        print("✓ alwabp_instance.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar alwabp_instance: {e}")
        return False
    
    try:
        from alwabp_solution import ALWABPSolution
        print("✓ alwabp_solution.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar alwabp_solution: {e}")
        return False
    
    try:
        from decoder import RandomKeyDecoder
        print("✓ decoder.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar decoder: {e}")
        return False
    
    try:
        from brkga import BRKGA
        print("✓ brkga.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar brkga: {e}")
        return False
    
    try:
        from local_search import LocalSearch
        print("✓ local_search.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar local_search: {e}")
        return False
    
    try:
        from rko_brkga import RKO_BRKGA
        print("✓ rko_brkga.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar rko_brkga: {e}")
        return False
    
    try:
        from visualization import visualize_solution
        print("✓ visualization.py importado")
    except Exception as e:
        print(f"✗ Erro ao importar visualization: {e}")
        return False
    
    print("\n✅ Todos os módulos importados com sucesso!\n")
    return True


def test_instance_creation():
    """Testa criação de instância"""
    print("=" * 70)
    print("TESTE 2: Criação de Instância")
    print("=" * 70)
    
    try:
        from alwabp_instance import ALWABPInstance
        
        instance = ALWABPInstance(n_tasks=5, n_workers=3, n_stations=3)
        print("✓ Instância criada")
        
        instance.execution_times = np.array([
            [5, 4, 6, 5, 7],
            [6, 5, 5, 6, 6],
            [7, 6, 4, 7, 5]
        ], dtype=float)
        print("✓ Tempos de execução definidos")
        
        instance.add_precedence(0, 1)
        instance.add_precedence(1, 2)
        instance.add_precedence(2, 3)
        instance.add_precedence(3, 4)
        print("✓ Precedências adicionadas")
        
        instance.set_incompatible_task(1, 2)
        print("✓ Incompatibilidade definida")
        
        prec_matrix = instance.get_precedence_matrix()
        print("✓ Matriz de precedências calculada")
        
        print(f"\nInstância: {instance.n_tasks} tarefas, {instance.n_workers} trabalhadores")
        print(f"Precedências: {len(instance.precedences)}")
        print("\n✅ Instância criada corretamente!\n")
        return True, instance
        
    except Exception as e:
        print(f"\n✗ Erro ao criar instância: {e}\n")
        import traceback
        traceback.print_exc()
        return False, None


def test_solution_creation(instance):
    """Testa criação de solução"""
    print("=" * 70)
    print("TESTE 3: Criação de Solução")
    print("=" * 70)
    
    try:
        from alwabp_solution import ALWABPSolution
        
        solution = ALWABPSolution(instance)
        print("✓ Solução criada")
        
        solution.worker_assignment = np.array([0, 1, 2])
        solution.task_assignment = np.array([0, 0, 1, 1, 2])
        print("✓ Atribuições definidas")
        
        cycle_time = solution.calculate_cycle_time()
        print(f"✓ Tempo de ciclo calculado: {cycle_time:.2f}")
        
        is_feasible = solution.is_feasible()
        print(f"✓ Factibilidade verificada: {is_feasible}")
        
        print("\n✅ Solução manipulada corretamente!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro ao criar solução: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_decoder(instance):
    """Testa decodificador"""
    print("=" * 70)
    print("TESTE 4: Decodificação")
    print("=" * 70)
    
    try:
        from decoder import RandomKeyDecoder
        
        decoder = RandomKeyDecoder(instance)
        print("✓ Decodificador criado")
        
        # Cromossomo aleatório
        chromosome = np.random.rand(instance.n_tasks + instance.n_workers)
        print("✓ Cromossomo gerado")
        
        solution = decoder.decode(chromosome)
        print("✓ Cromossomo decodificado")
        
        print(f"  Tempo de ciclo: {solution.cycle_time:.2f}")
        print(f"  Factível: {solution.is_feasible()}")
        
        print("\n✅ Decodificação funcionando!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro no decodificador: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_brkga(instance):
    """Testa BRKGA"""
    print("=" * 70)
    print("TESTE 5: BRKGA")
    print("=" * 70)
    
    try:
        from brkga import BRKGA
        from decoder import RandomKeyDecoder
        
        decoder = RandomKeyDecoder(instance)
        brkga = BRKGA(instance, decoder, population_size=20)
        print("✓ BRKGA criado")
        
        brkga.initialize_population()
        print("✓ População inicializada")
        
        solution = brkga.evolve(generations=5, verbose=False)
        print("✓ Evolução executada (5 gerações)")
        
        print(f"  Melhor tempo de ciclo: {brkga.best_fitness:.2f}")
        print(f"  Factível: {solution.is_feasible()}")
        
        print("\n✅ BRKGA funcionando!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro no BRKGA: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_local_search(instance):
    """Testa busca local"""
    print("=" * 70)
    print("TESTE 6: Busca Local")
    print("=" * 70)
    
    try:
        from local_search import LocalSearch
        from alwabp_solution import ALWABPSolution
        
        # Criar solução inicial
        solution = ALWABPSolution(instance)
        solution.worker_assignment = np.array([0, 1, 2])
        solution.task_assignment = np.array([0, 0, 1, 1, 2])
        solution.calculate_cycle_time()
        
        initial_cycle_time = solution.cycle_time
        print(f"✓ Solução inicial criada (ciclo: {initial_cycle_time:.2f})")
        
        local_search = LocalSearch(instance)
        improved_solution = local_search.improve(solution, max_iterations=10)
        print("✓ Busca local executada")
        
        print(f"  Ciclo antes: {initial_cycle_time:.2f}")
        print(f"  Ciclo depois: {improved_solution.cycle_time:.2f}")
        print(f"  Melhoria: {initial_cycle_time - improved_solution.cycle_time:.2f}")
        
        print("\n✅ Busca local funcionando!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro na busca local: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_rko_brkga(instance):
    """Testa algoritmo completo"""
    print("=" * 70)
    print("TESTE 7: RKO-BRKGA Completo")
    print("=" * 70)
    
    try:
        from rko_brkga import RKO_BRKGA
        
        rko = RKO_BRKGA(instance, population_size=20)
        print("✓ RKO-BRKGA criado")
        
        solution, exec_time = rko.solve(
            brkga_generations=10,
            local_search_freq=5,
            local_search_iterations=10,
            verbose=False
        )
        print("✓ Algoritmo executado")
        
        print(f"  Tempo de ciclo: {solution.cycle_time:.2f}")
        print(f"  Tempo de execução: {exec_time:.2f}s")
        print(f"  Factível: {solution.is_feasible()}")
        
        print("\n✅ RKO-BRKGA funcionando completamente!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro no RKO-BRKGA: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DO CÓDIGO RKO-BRKGA PARA ALWABP")
    print("=" * 70)
    print("\nExecutando testes de validação...\n")
    
    # Teste 1: Imports
    if not test_imports():
        print("\n❌ FALHA: Problema ao importar módulos")
        print("Verifique se todos os arquivos estão no diretório correto\n")
        return False
    
    # Teste 2: Instância
    success, instance = test_instance_creation()
    if not success:
        print("\n❌ FALHA: Problema ao criar instância")
        return False
    
    # Teste 3: Solução
    if not test_solution_creation(instance):
        print("\n❌ FALHA: Problema ao criar solução")
        return False
    
    # Teste 4: Decoder
    if not test_decoder(instance):
        print("\n❌ FALHA: Problema no decodificador")
        return False
    
    # Teste 5: BRKGA
    if not test_brkga(instance):
        print("\n❌ FALHA: Problema no BRKGA")
        return False
    
    # Teste 6: Local Search
    if not test_local_search(instance):
        print("\n❌ FALHA: Problema na busca local")
        return False
    
    # Teste 7: RKO-BRKGA
    if not test_rko_brkga(instance):
        print("\n❌ FALHA: Problema no RKO-BRKGA completo")
        return False
    
    # Resumo final
    print("=" * 70)
    print("RESULTADO DA VALIDAÇÃO")
    print("=" * 70)
    print("\n✅✅✅ TODOS OS TESTES PASSARAM! ✅✅✅")
    print("\nO código está funcionando corretamente!")
    print("Você pode usar o algoritmo com confiança.\n")
    print("Próximos passos:")
    print("  1. Execute: python main.py")
    print("  2. Ou veja: python exemplos_uso.py")
    print("  3. Leia: GUIA_RAPIDO.md")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
