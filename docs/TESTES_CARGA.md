# 🔥 Guia de Testes de Carga e Performance

Este guia documenta como executar e interpretar testes de carga e performance do projeto.

---

## 📊 Testes de Carga com Locust

### O que é Locust?

Locust é uma ferramenta de teste de carga que simula múltiplos usuários acessando a aplicação simultaneamente. Permite identificar gargalos de performance e validar comportamento sob carga.

### Cenários Disponíveis

O arquivo `tests/load/locustfile.py` define 4 cenários:

1. **ChatbotUser** - Simula usuários fazendo perguntas (peso: chat=10, health=2, metrics=1)
2. **HealthCheckUser** - Simula monitoramento constante (apenas health checks)
3. **MixedUser** - Uso misto mais realista (chat=15, config=3, health=2, metrics=1)
4. **StressTestUser** - Teste de stress com requisições rápidas (0.1-0.5s entre requisições)

### Como Executar

#### 1. Interface Web (Recomendado)

```bash
# Inicie o servidor em um terminal
uvicorn src.backend.api:app --host 0.0.0.0 --port 8000

# Em outro terminal, inicie o Locust
make test-load-ui
# ou
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

Acesse http://localhost:8089 e configure:
- **Number of users**: 50-100 (usuários simultâneos)
- **Spawn rate**: 5-10 (usuários/segundo)
- **Host**: http://localhost:8000

#### 2. Modo Headless (CI/CD)

```bash
# Teste rápido (50 usuários, 60 segundos)
make test-load

# Teste personalizado
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 120s --headless
```

### Métricas Importantes

- **RPS (Requests Per Second)**: Throughput da aplicação
- **Response Time (p50, p95, p99)**: Latência em percentis
- **Failure Rate**: Taxa de erros
- **Users**: Número de usuários simultâneos

### Metas de Performance

| Métrica | Meta | Crítico |
|:---|:---:|:---:|
| **Throughput** | > 50 req/s | > 100 req/s |
| **p95 Response Time** | < 2s | < 5s |
| **p99 Response Time** | < 5s | < 10s |
| **Failure Rate** | < 1% | < 5% |
| **Concurrent Users** | 50+ | 100+ |

---

## ⚡ Benchmarks de Performance com pytest-benchmark

### O que é pytest-benchmark?

pytest-benchmark mede o tempo de execução de funções específicas, permitindo detectar regressões de performance.

### Testes Disponíveis

O arquivo `tests/performance/test_benchmarks.py` inclui:

1. **test_pipeline_performance** - Pipeline completo (meta: < 30s)
2. **test_cache_performance** - Operações de cache (meta: < 10ms)
3. **test_validation_performance** - Validação de entrada (meta: < 1ms)
4. **test_formatter_performance** - Formatação de resposta (meta: < 100ms)
5. **test_metrics_collection_performance** - Coleta de métricas (meta: < 1ms)
6. **test_concurrent_requests_performance** - 10 requisições concorrentes (meta: < 5s)

### Como Executar

#### 1. Benchmarks Simples

```bash
# Executar todos os benchmarks
make test-benchmark

# Executar benchmark específico
pytest tests/performance/test_benchmarks.py::test_cache_performance --benchmark-only -v
```

#### 2. Benchmarks com Comparação

```bash
# Primeira execução (salva baseline)
make test-benchmark-compare

# Execuções futuras (compara com baseline)
make test-benchmark-compare
```

#### 3. Ver Histórico

```bash
# Listar execuções salvas
pytest-benchmark list

# Comparar duas execuções específicas
pytest-benchmark compare 0001 0002
```

### Interpretando Resultados

```
Name (time in ms)                    Min      Max     Mean  StdDev  Median
test_cache_performance              5.23     8.91     6.12    0.89    5.98
test_validation_performance         0.45     1.23     0.67    0.21    0.61
```

- **Min/Max**: Tempo mínimo/máximo de execução
- **Mean**: Tempo médio
- **StdDev**: Desvio padrão (menor = mais consistente)
- **Median**: Mediana (menos afetada por outliers)

### Metas de Performance

| Teste | Meta | Crítico |
|:---|:---:|:---:|
| **Pipeline** | < 30s | < 60s |
| **Cache** | < 10ms | < 50ms |
| **Validation** | < 1ms | < 5ms |
| **Formatter** | < 100ms | < 500ms |
| **Metrics** | < 1ms | < 5ms |
| **Concurrent (10 req)** | < 5s | < 10s |

---

## 🎯 Quando Executar

### Testes de Carga (Locust)

- ✅ Antes de deploy em produção
- ✅ Após mudanças significativas na API
- ✅ Periodicamente (mensal) para validar escalabilidade
- ✅ Ao investigar problemas de performance

### Benchmarks (pytest-benchmark)

- ✅ Antes de cada commit (CI/CD)
- ✅ Ao otimizar código
- ✅ Para detectar regressões de performance
- ✅ Ao comparar implementações alternativas

---

## 🚨 Troubleshooting

### Locust

**Problema**: "Connection refused"
- **Solução**: Certifique-se de que o servidor está rodando em http://localhost:8000

**Problema**: Taxa de erro muito alta
- **Solução**: Verifique logs do servidor, pode ser rate limiting ou timeout

**Problema**: Response time muito alto
- **Solução**: Reduza número de usuários ou aumente recursos do servidor

### pytest-benchmark

**Problema**: Resultados inconsistentes
- **Solução**: Execute múltiplas vezes, use `--benchmark-warmup`

**Problema**: Testes muito lentos
- **Solução**: Use mocks para dependências externas (LLM, etc)

---

## 📝 Boas Práticas

1. **Sempre execute testes de carga em ambiente isolado** (não em produção)
2. **Use mocks para LLMs** em benchmarks (para resultados consistentes)
3. **Monitore recursos do sistema** (CPU, memória, rede) durante testes de carga
4. **Salve baselines** de benchmarks para comparação futura
5. **Documente mudanças** que causam regressões de performance

---

## 🔗 Recursos Adicionais

- [Documentação Locust](https://docs.locust.io/)
- [Documentação pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [Guia de Performance Testing](https://martinfowler.com/articles/practical-test-pyramid.html#PerformanceTests)

---

**Última atualização**: 2025-11-26
