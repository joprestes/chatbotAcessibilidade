from chatbot_acessibilidade.agents.factory import criar_agentes

def test_criar_agentes_inclui_refatorador():
    """Verifica se o agente refatorador é criado corretamente."""
    agentes = criar_agentes()
    
    assert "refatorador" in agentes
    agent = agentes["refatorador"]
    assert agent.name == "refatorador_codigo_acessivel"
    assert "Especialista em Refatoração" in agent.instruction
    assert "WCAG 2.2 AAA" in agent.instruction
    assert "OUTPUT: Um JSON estrito" in agent.instruction

def test_todos_agentes_tem_instrucoes():
    """Garante que todos os agentes têm instruções definidas."""
    agentes = criar_agentes()
    for nome, agente in agentes.items():
        assert agente.instruction is not None
        assert len(agente.instruction) > 10
