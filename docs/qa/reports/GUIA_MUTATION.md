# 🧬 Guia de Mutation Testing

## O que é Mutation Testing?

**Mutation Testing** é uma técnica que valida a qualidade dos seus testes introduzindo pequenas mudanças (mutações) no código e verificando se os testes detectam essas mudanças.

### Como Funciona

1. **Mutmut gera mutantes**: Pequenas alterações no código (ex: `>` vira `>=`, `+` vira `-`)
2. **Testes são executados**: Para cada mutante
3. **Resultado**:
   - ✅ **Killed**: Teste detectou a mutação (bom!)
   - ❌ **Survived**: Teste não detectou a mutação (teste fraco!)
   - ⏭️ **Skipped**: Mutação não aplicável
   - ⚠️ **Timeout**: Teste demorou muito

### Mutation Score

```
Mutation Score = (Mutantes Killed / Total de Mutantes) × 100%
```

**Meta**: > 80% (excelente qualidade de testes)

---

## 🚀 Como Executar

### Instalação

```bash
pip install mutmut
# ou
make install
```

### Execução Básica

```bash
# Executar mutation testing em módulo específico
make test-mutation

# Executar em arquivo específico
mutmut run src/chatbot_acessibilidade/core/validators.py

# Ver resultados
make mutation-results
```

### Ver Resultados

```bash
# Resumo dos resultados
mutmut results

# Ver mutantes que sobreviveram
mutmut show survived

# Ver mutante específico
mutmut show 1

# Aplicar mutante para debug
mutmut apply 1
```

### Comandos Úteis

```bash
# Limpar resultados anteriores
make mutation-clean

# Ver relatório HTML
mutmut html
open html/index.html
```

---

## 📊 Interpretando Resultados

### Exemplo de Output

```
Survived 🙁: 5
Killed ✅: 45
Timeout ⏰: 0
Suspicious 🤔: 0
Skipped 🔇: 10
Total: 60

Mutation Score: 90.0%
```

### O que fazer com mutantes que sobreviveram?

1. **Ver o mutante**: `mutmut show <id>`
2. **Entender a mutação**: O que foi alterado?
3. **Adicionar teste**: Criar teste que detecte essa mudança
4. **Re-executar**: Verificar se o mutante agora é killed

---

## 🎯 Módulos Prioritários

Execute mutation testing nestes módulos críticos primeiro:

### 1. Validators (`src/chatbot_acessibilidade/core/validators.py`)
```bash
mutmut run src/chatbot_acessibilidade/core/validators.py
```

**Por quê**: Segurança crítica (sanitização, validação)

### 2. Cache (`src/chatbot_acessibilidade/core/cache.py`)
```bash
mutmut run src/chatbot_acessibilidade/core/cache.py
```

**Por quê**: Performance crítica

### 3. Formatter (`src/chatbot_acessibilidade/core/formatter.py`)
```bash
mutmut run src/chatbot_acessibilidade/core/formatter.py
```

**Por quê**: Lógica de formatação de resposta

### 4. Pipeline (`src/chatbot_acessibilidade/pipeline/orquestrador.py`)
```bash
mutmut run src/chatbot_acessibilidade/pipeline/orquestrador.py
```

**Por quê**: Orquestração crítica

---

## 🔧 Configuração

### `.mutmut-config.py`

```python
def pre_mutation(context):
    """Pula mutações em imports"""
    if context.current_source_line.strip().startswith('import '):
        context.skip = True
    if context.current_source_line.strip().startswith('from '):
        context.skip = True
```

### Opções Úteis

```bash
# Usar cobertura para focar em código testado
--use-coverage

# Executar apenas testes relevantes
--runner="pytest -x -q"

# Limitar número de mutantes (para teste rápido)
--max-mutations=10

# Executar em paralelo
--processes=4
```

---

## 📈 Metas de Mutation Score

| Módulo | Meta | Crítico |
|:---|:---:|:---:|
| **validators.py** | > 90% | > 80% |
| **cache.py** | > 85% | > 75% |
| **formatter.py** | > 80% | > 70% |
| **orquestrador.py** | > 85% | > 75% |
| **Geral** | > 80% | > 70% |

---

## 🚨 Troubleshooting

### Problema: Mutation testing muito lento
**Solução**: 
- Use `--use-coverage` para focar em código testado
- Use `--processes=4` para paralelização
- Execute em módulos específicos, não em todo o código

### Problema: Muitos mutantes sobreviveram
**Solução**:
- Normal na primeira execução
- Foque nos mutantes mais importantes
- Adicione testes incrementalmente

### Problema: Timeout em testes
**Solução**:
- Aumente timeout: `--timeout-factor=2.0`
- Otimize testes lentos
- Use mocks para dependências externas

---

## 💡 Boas Práticas

1. **Execute incrementalmente**: Comece com módulos pequenos
2. **Foque no crítico**: Validators, cache, pipeline primeiro
3. **Não busque 100%**: 80-90% é excelente
4. **Use coverage**: `--use-coverage` economiza tempo
5. **Documente mutantes ignorados**: Alguns são aceitáveis
6. **Integre no CI**: Execute periodicamente (semanal)

---

## 📝 Workflow Recomendado

```bash
# 1. Executar em módulo crítico
mutmut run src/chatbot_acessibilidade/core/validators.py

# 2. Ver resultados
mutmut results

# 3. Analisar sobreviventes
mutmut show survived

# 4. Para cada sobrevivente importante:
#    - Ver mutação: mutmut show <id>
#    - Adicionar teste
#    - Re-executar

# 5. Gerar relatório
mutmut html
open html/index.html
```

---

## 🔗 Recursos

- [Documentação mutmut](https://mutmut.readthedocs.io/)
- [Mutation Testing Explained](https://en.wikipedia.org/wiki/Mutation_testing)
- [Best Practices](https://github.com/boxed/mutmut#best-practices)

---

**Última atualização**: 2025-11-26
