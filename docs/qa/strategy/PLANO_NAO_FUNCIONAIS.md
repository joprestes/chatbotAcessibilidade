# 🚀 Plano de Testes Não-Funcionais (Performance e Segurança)

**Projeto:** Chatbot de Acessibilidade Digital (Ada)
**Versão:** 1.0
**Classificação:** Uso Interno / Confidencial
**Referência:** ISO/IEC 25010 (Eficiência de Performance e Segurança)

---

## 1. Introdução
Enquanto os testes funcionais garantem que o sistema "faz o que deve fazer", este plano foca em "como o sistema se comporta" sob condições de estresse e ataques. Em ambientes regulados, a validação de **NFRs (Non-Functional Requirements)** é mandatória para mitigar riscos operacionais e legais.

---

## 2. Estratégia de Testes de Performance

### 2.1 Ferramentas
*   **Locust:** Para simulação de carga de usuários (Python-based).
*   **Pytest-Benchmark:** Para micro-benchmarks de funções críticas.

### 2.2 Cenários de Teste de Carga

| ID | Tipo de Teste | Descrição | Carga (Usuários) | Duração | Critério de Aceite (KPI) |
|:---|:---|:---|:---|:---|:---|
| **PERF-01** | **Load Test** | Simular uso normal esperado. | 50 usuários simultâneos (Ramp-up 1/s) | 10 min | Latência p95 < 500ms. Erro < 1%. |
| **PERF-02** | **Stress Test** | Encontrar o ponto de quebra. | 200+ usuários (Ramp-up 5/s) | Até falha | Identificar gargalo (CPU/RAM/DB). Recuperação automática após fim do teste. |
| **PERF-03** | **Spike Test** | Picos repentinos de tráfego. | 0 -> 100 usuários em 10s | 5 min | Sistema não deve travar (500). Pode degradar performance, mas não cair. |
| **PERF-04** | **Soak Test** | Teste de resistência (Memory Leak). | 20 usuários constantes | 4 horas | Uso de RAM estável. Sem degradação progressiva de latência. |

### 2.3 Métricas de Sucesso (SLAs)
*   **Tempo de Resposta (API):** < 200ms (p95) para endpoints simples.
*   **Tempo de Resposta (LLM):** < 5s (p95) para streaming completo.
*   **Throughput:** Suportar mínimo de 100 RPM (Requests Per Minute).

---

## 3. Estratégia de Testes de Segurança (AppSec)

### 3.1 Ferramentas
*   **OWASP ZAP (Zed Attack Proxy):** DAST (Dynamic Application Security Testing).
*   **SonarQube / Bandit:** SAST (Static Application Security Testing) para Python.
*   **Dependabot/Snyk:** Análise de vulnerabilidades em dependências (SCA).

### 3.2 Cenários de Segurança (OWASP Top 10)

| ID | Vulnerabilidade | Teste Executado | Resultado Esperado |
|:---|:---|:---|:---|
| **SEC-01** | **Injection (SQL/NoSQL)** | Tentar injetar payloads SQL em inputs de busca/chat. | API rejeita ou sanitiza. Retorna 400/422. |
| **SEC-02** | **XSS (Cross-Site Scripting)** | Injetar scripts JS (`<script>`) no chat. | Frontend renderiza como texto plano (escaped). |
| **SEC-03** | **Broken Access Control** | Tentar acessar endpoints administrativos sem token. | Retorna 401 Unauthorized ou 403 Forbidden. |
| **SEC-04** | **Sensitive Data Exposure** | Verificar headers de resposta e logs. | Sem exposição de PII, Tokens ou Stack Traces em produção. |
| **SEC-05** | **Rate Limiting** | Ataque de força bruta / DoS. | Bloqueio de IP após N tentativas (429 Too Many Requests). |

---

## 4. Observabilidade e Monitoramento
Para garantir que os testes reflitam a realidade e para monitoramento contínuo em produção.

*   **Logs Estruturados:** JSON logs com Trace ID para rastreabilidade distribuída.
*   **Métricas:** Monitoramento de latência, erros e saturação de recursos (CPU/Memória).
*   **Alertas:** Notificação imediata para Latência > SLA ou Error Rate > 1%.

---

## 5. Plano de Execução e Automação

*   **Pipeline de CI:**
    *   SAST (Bandit) roda em todo PR.
    *   Smoke Performance (Benchmark) roda em todo PR.
*   **Pipeline de CD (Staging):**
    *   DAST (OWASP ZAP) roda nightly.
    *   Load Test (Locust) roda antes de release major.

---
*Este plano garante que o Chatbot Ada não apenas funcione, mas opere com alta performance e segurança, protegendo os dados dos usuários e a reputação da organização.*
