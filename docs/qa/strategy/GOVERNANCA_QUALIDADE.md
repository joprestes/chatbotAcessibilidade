# 🏛️ Estratégia de Qualidade e Governança (QA Governance)

**Projeto:** Chatbot de Acessibilidade Digital (Ada)
**Versão:** 1.0
**Classificação:** Uso Interno / Confidencial

---

## 1. Visão Geral
Este documento estabelece as diretrizes de governança, processos e métricas para garantir a qualidade do software, alinhado com práticas de **Indústrias Reguladas** (ex: Saúde, Finanças) e metodologias **Ágeis**.

---

## 2. Matriz de Rastreabilidade (Traceability Matrix)
Garante que todos os requisitos tenham cobertura de teste e que todos os defeitos estejam ligados a um caso de teste.

| ID Requisito | Descrição | ID Caso de Teste | Tipo de Teste | ID Defeito (Se houver) |
|:---|:---|:---|:---|:---|
| **REQ-01** | Envio de Mensagens | SMK-02, CT-02 | Funcional / Smoke | - |
| **REQ-02** | Limpar Histórico | CT-01 | Funcional | BUG-001 (Resolvido) |
| **REQ-03** | Acessibilidade (WCAG) | ACC-01 a ACC-05 | Manual / Compliance | - |
| **REQ-04** | Resiliência de Rede | EXC-01 | Exceção | - |
| **REQ-05** | Segurança (XSS/Input) | EDG-03, EDG-04 | Segurança | - |

---

## 3. Critérios de Aceite e Saída (Entry & Exit Criteria)

### 3.1 Critérios de Entrada (Definition of Ready for QA)
*   [ ] Código versionado no Git e mergeado na branch de feature.
*   [ ] Testes unitários passando com cobertura > 80%.
*   [ ] Ambiente de teste (Staging/Local) estável e acessível.
*   [ ] Smoke Test executado com sucesso pelo desenvolvedor.

### 3.2 Critérios de Saída (Definition of Done for QA)
*   [ ] 100% dos casos de teste planejados executados.
*   [ ] Zero defeitos Críticos ou Altos abertos.
*   [ ] Defeitos Médios/Baixos documentados e com workaround conhecido.
*   [ ] Relatório de Testes (Test Summary Report) aprovado pelo QA Lead.
*   [ ] Validação de Acessibilidade (WCAG AAA) concluída.

---

## 4. Gestão de Defeitos (Defect Lifecycle)

### 4.1 Fluxo de Status
`New` -> `Open` -> `In Progress` -> `Resolved` -> `Verified` -> `Closed`

### 4.2 Matriz de Severidade vs. Prioridade

| Severidade | Descrição | SLA de Resolução |
|:---|:---|:---|
| **Crítica (Blocker)** | Sistema inoperante, perda de dados, falha de segurança. | Imediato (Hotfix) |
| **Alta (Major)** | Funcionalidade principal quebrada, sem workaround. | 24 horas |
| **Média (Minor)** | Funcionalidade secundária com falha, existe workaround. | Próxima Sprint |
| **Baixa (Trivial)** | Erro cosmético, ortografia, melhoria de UI. | Backlog |

---

## 5. Métricas de Qualidade (KPIs)
Para monitoramento contínuo da saúde do projeto.

1.  **Densidade de Defeitos:** (Total de Defeitos / KLOC ou Pontos de Função).
2.  **Taxa de Sucesso de Testes:** (Testes Passaram / Total Executados) * 100. *Meta: > 95%*.
3.  **Cobertura de Requisitos:** (Requisitos Testados / Total Requisitos) * 100. *Meta: 100%*.
4.  **MTTR (Mean Time To Resolve):** Tempo médio para correção de bugs críticos.

---

## 6. Gestão de Riscos (Risk Management)

| Risco | Impacto | Probabilidade | Mitigação |
|:---|:---|:---|:---|
| **Regressão em Acessibilidade** | Alto (Legal/Reputação) | Média | Automação com `axe-core` no CI/CD + Auditoria Manual. |
| **Indisponibilidade de LLM Externo** | Alto (Funcional) | Média | Implementação de Fallback e tratamento de erros gracioso. |
| **Vazamento de Dados (PII)** | Crítico (Legal) | Baixa | Sanitização rigorosa de inputs e logs (LGPD). |

---

## 7. Conformidade e Auditoria
Este projeto segue as diretrizes:
*   **WCAG 2.2 Nível AAA** (Acessibilidade Web).
*   **OWASP Top 10** (Segurança de Aplicações Web).
*   **ISO/IEC 25010** (Qualidade de Produto de Software).

---
*Documento vivo, sujeito a revisões periódicas pelo time de Governança de TI.*
