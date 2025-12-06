#!/usr/bin/env python3
"""
Script de entrada para executar o RKO-BRKGA

Este script chama o main.py dentro de Program/Main/
"""

import sys
import os

# Adicionar diretórios ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'Program', 'Main'))
sys.path.insert(0, os.path.join(project_root, 'Program', 'MH'))
sys.path.insert(0, os.path.join(project_root, 'Program', 'Problem'))

# Importar e executar main
from main import main

if __name__ == "__main__":
    main()
