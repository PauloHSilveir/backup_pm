# 📑 Índice de Arquivos - RKO-BRKGA para ALWABP

## 🎯 Começando

| Arquivo | Descrição | Quando Ler |
|---------|-----------|------------|
| **GUIA_RAPIDO.md** | Guia de início rápido (5 min) | 🟢 Comece aqui! |
| **README.md** | Visão geral do projeto | 🟢 Logo depois |
| **README_RKO.md** | Documentação completa do código | 🟡 Para usar o código |

## 📚 Documentação Teórica

| Arquivo | Descrição | Quando Ler |
|---------|-----------|------------|
| **METODOLOGIA.md** | Fundamentação teórica e algoritmos | 🟡 Para entender a teoria |
| **ESTRUTURA_MODULAR.md** | Explicação da arquitetura do código | 🟡 Para entender o design |
| **Enunciado.pdf** | Problema original ALWABP | 🔵 Referência do problema |

## 💻 Código Principal

### Camada de Domínio
| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `alwabp_instance.py` | ~120 | Representação de instâncias do problema |
| `alwabp_solution.py` | ~90 | Representação de soluções |

### Camada de Algoritmo
| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `decoder.py` | ~170 | Decodificador de chaves aleatórias |
| `brkga.py` | ~150 | Implementação do BRKGA |
| `local_search.py` | ~270 | Busca local para refinamento |
| `rko_brkga.py` | ~260 | Algoritmo híbrido principal |

### Camada de Aplicação
| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `main.py` | ~180 | Script de execução interativa |
| `exemplos_uso.py` | ~570 | 5 exemplos práticos diferentes |
| `test_experiments.py` | ~260 | Testes e benchmarks |
| `visualization.py` | ~380 | Funções de visualização |

## 🚀 Executáveis

### Para Usuários
```bash
python main.py              # Uso interativo básico
python exemplos_uso.py      # Ver casos práticos
```

### Para Desenvolvedores/Pesquisadores
```bash
python test_experiments.py  # Experimentos científicos
```

## 📊 Tamanho do Projeto

| Métrica | Valor |
|---------|-------|
| **Arquivos Python** | 10 |
| **Linhas de código** | ~2450 |
| **Arquivos Markdown** | 6 |
| **Classes principais** | 6 |
| **Exemplos práticos** | 5 |

## 🗺️ Mapa de Navegação Rápida

### Quero usar o algoritmo
```
GUIA_RAPIDO.md → main.py → exemplos_uso.py
```

### Quero entender o código
```
README_RKO.md → ESTRUTURA_MODULAR.md → Código fonte
```

### Quero entender a teoria
```
METODOLOGIA.md → Enunciado.pdf → Papers referenciados
```

### Quero fazer experimentos
```
test_experiments.py → METODOLOGIA.md (seção de parâmetros)
```

### Quero modificar/estender
```
ESTRUTURA_MODULAR.md (seção "Como Estender") → Código específico
```

## 📖 Ordem de Leitura Recomendada

### Nível Iniciante
1. ✅ GUIA_RAPIDO.md (5 min)
2. ✅ README.md (2 min)
3. ✅ Executar `python main.py` (5 min)
4. ✅ README_RKO.md (15 min)
5. ✅ Executar `python exemplos_uso.py` (10 min)

**Total**: ~37 minutos para começar a usar

### Nível Intermediário
1. ✅ Tudo do nível iniciante
2. ✅ ESTRUTURA_MODULAR.md (20 min)
3. ✅ Ler `alwabp_instance.py` e `alwabp_solution.py` (10 min)
4. ✅ Ler `decoder.py` (15 min)
5. ✅ METODOLOGIA.md (30 min)

**Total**: +75 minutos para entender profundamente

### Nível Avançado
1. ✅ Tudo dos níveis anteriores
2. ✅ Ler `brkga.py` (20 min)
3. ✅ Ler `local_search.py` (20 min)
4. ✅ Ler `rko_brkga.py` (25 min)
5. ✅ Executar `python test_experiments.py` (20 min)
6. ✅ Estudar Enunciado.pdf e papers (60 min)

**Total**: +145 minutos para domínio completo

## 🎓 Por Objetivo

### Objetivo: Usar em Trabalho/Projeto
- GUIA_RAPIDO.md
- main.py
- exemplos_uso.py
- README_RKO.md

### Objetivo: Entender para TCC/Dissertação
- Tudo acima +
- METODOLOGIA.md
- ESTRUTURA_MODULAR.md
- Código fonte completo
- Enunciado.pdf

### Objetivo: Publicar Paper
- Tudo acima +
- test_experiments.py
- Modificar e estender código
- Comparar com outros algoritmos

### Objetivo: Ensinar/Apresentar
- README.md
- METODOLOGIA.md (apresentação teórica)
- exemplos_uso.py (demonstração prática)
- visualization.py (gerar figuras)

## 🔍 Busca Rápida

### Como fazer X?

| Tarefa | Ver Arquivo |
|--------|-------------|
| Criar instância | GUIA_RAPIDO.md, alwabp_instance.py |
| Executar algoritmo | GUIA_RAPIDO.md, main.py |
| Ajustar parâmetros | GUIA_RAPIDO.md, METODOLOGIA.md |
| Visualizar solução | GUIA_RAPIDO.md, visualization.py |
| Comparar soluções | exemplos_uso.py, visualization.py |
| Entender BRKGA | METODOLOGIA.md, brkga.py |
| Entender busca local | METODOLOGIA.md, local_search.py |
| Adicionar movimento | ESTRUTURA_MODULAR.md, local_search.py |
| Fazer experimentos | test_experiments.py |
| Ler de arquivo | alwabp_instance.py (implementar) |

## 📦 Dependências Externas

| Biblioteca | Versão | Uso |
|------------|--------|-----|
| numpy | >= 1.19 | Operações matriciais e arrays |

**Instalação**: `pip install numpy`

## 🆘 Troubleshooting

| Problema | Ver |
|----------|-----|
| Não sei por onde começar | GUIA_RAPIDO.md |
| Erro ao executar | GUIA_RAPIDO.md (seção Instalação) |
| Não entendo o algoritmo | METODOLOGIA.md |
| Não entendo o código | ESTRUTURA_MODULAR.md |
| Resultados ruins | GUIA_RAPIDO.md (seção Ajustar Parâmetros) |
| Execução lenta | GUIA_RAPIDO.md (dicas de performance) |
| Solução infactível | GUIA_RAPIDO.md (dicas de debugging) |

## 📞 Hierarquia de Ajuda

```
1. GUIA_RAPIDO.md
   ↓ (se não resolver)
2. README_RKO.md
   ↓ (se não resolver)
3. ESTRUTURA_MODULAR.md
   ↓ (se não resolver)
4. Código fonte com comentários
   ↓ (se não resolver)
5. METODOLOGIA.md + Papers
```

## ✨ Destaques

### Arquivos Essenciais (Não Pule!)
- ⭐ GUIA_RAPIDO.md
- ⭐ README_RKO.md
- ⭐ main.py
- ⭐ rko_brkga.py

### Arquivos para Referência
- 📚 METODOLOGIA.md
- 📚 ESTRUTURA_MODULAR.md
- 📚 Enunciado.pdf

### Arquivos para Aprendizado
- 🎓 exemplos_uso.py
- 🎓 test_experiments.py
- 🎓 visualization.py

## 🗂️ Organização por Tipo

### Documentação (6 arquivos)
- README.md
- README_RKO.md
- GUIA_RAPIDO.md
- METODOLOGIA.md
- ESTRUTURA_MODULAR.md
- Enunciado.pdf

### Código Core (6 arquivos)
- alwabp_instance.py
- alwabp_solution.py
- decoder.py
- brkga.py
- local_search.py
- rko_brkga.py

### Aplicações (4 arquivos)
- main.py
- exemplos_uso.py
- test_experiments.py
- visualization.py

### Outros
- bygpt.py (arquivo pré-existente)
- formato_instancia.txt (arquivo pré-existente)

---

**Última Atualização**: Dezembro 2025
**Versão**: 1.0
**Autor**: Paulo H. Silveira
