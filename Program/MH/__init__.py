"""
GENERAL_CODE - Meta-heurística BRKGA com Busca Local

Este módulo contém a implementação da meta-heurística:
- BRKGA (Biased Random-Key Genetic Algorithm)
- Busca Local (Local Search)
- Pool de Elite (Elite Pool)
- Integração RKO-BRKGA
"""

from .brkga import BRKGA
from .local_search import LocalSearch
from .elite_pool import ElitePool
from .rko_brkga import RKO_BRKGA

__all__ = [
    'BRKGA',
    'LocalSearch',
    'ElitePool',
    'RKO_BRKGA'
]
