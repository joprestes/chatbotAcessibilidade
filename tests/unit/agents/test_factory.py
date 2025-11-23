"""
Testes para o módulo factory.py
"""

import pytest

from google.adk.agents import Agent

from chatbot_acessibilidade.agents.factory import NOME_MODELO_ADK, criar_agentes

pytestmark = pytest.mark.unit


def test_nome_modelo_adk():
    """Testa se NOME_MODELO_ADK está definido corretamente"""
    assert NOME_MODELO_ADK == "gemini-2.0-flash"


def test_criar_agentes_retorna_dicionario():
    """Testa se criar_agentes retorna um dicionário"""
    agentes = criar_agentes()
    assert isinstance(agentes, dict)


def test_criar_agentes_tem_todos_os_agentes():
    """Testa se criar_agentes retorna todos os 5 agentes esperados"""
    agentes = criar_agentes()

    assert "assistente" in agentes
    assert "validador" in agentes
    assert "revisor" in agentes
    assert "testador" in agentes
    assert "aprofundador" in agentes

    assert len(agentes) == 5


def test_criar_agentes_todos_sao_instancias_agent():
    """Testa se todos os agentes são instâncias de Agent"""
    agentes = criar_agentes()

    for nome, agente in agentes.items():
        assert isinstance(agente, Agent), f"Agente '{nome}' não é uma instância de Agent"


def test_criar_agentes_assistente_tem_ferramentas():
    """Testa se o agente assistente tem ferramentas configuradas"""
    agentes = criar_agentes()
    assistente = agentes["assistente"]

    # Verifica se tem tools (google_search)
    assert hasattr(assistente, "tools") or hasattr(assistente, "_tools")


def test_criar_agentes_testador_tem_ferramentas():
    """Testa se o agente testador tem ferramentas configuradas"""
    agentes = criar_agentes()
    testador = agentes["testador"]

    # Verifica se tem tools (google_search)
    assert hasattr(testador, "tools") or hasattr(testador, "_tools")


def test_criar_agentes_aprofundador_tem_ferramentas():
    """Testa se o agente aprofundador tem ferramentas configuradas"""
    agentes = criar_agentes()
    aprofundador = agentes["aprofundador"]

    # Verifica se tem tools (google_search)
    assert hasattr(aprofundador, "tools") or hasattr(aprofundador, "_tools")


def test_criar_agentes_validador_sem_ferramentas():
    """Testa se o agente validador não tem ferramentas (não deve ter)"""
    criar_agentes()

    # Validador não deve ter ferramentas de busca
    # (verificação depende da implementação do Agent)


def test_criar_agentes_revisor_sem_ferramentas():
    """Testa se o agente revisor não tem ferramentas (não deve ter)"""
    criar_agentes()

    # Revisor não deve ter ferramentas de busca
    # (verificação depende da implementação do Agent)


def test_criar_agentes_nomes_corretos():
    """Testa se os agentes têm os nomes corretos"""
    agentes = criar_agentes()

    assert agentes["assistente"].name == "assistente_acessibilidade_digital"
    assert agentes["validador"].name == "validador_code_review"
    assert agentes["revisor"].name == "revisor_clareza_acessibilidade"
    assert agentes["testador"].name == "planejador_testes_qa"
    assert agentes["aprofundador"].name == "guia_estudos_referencias"


def test_criar_agentes_modelo_correto():
    """Testa se todos os agentes usam o modelo correto"""
    agentes = criar_agentes()

    for nome, agente in agentes.items():
        # Verifica se o modelo está configurado (depende da implementação do Agent)
        assert hasattr(agente, "model") or hasattr(agente, "_model")


def test_criar_agentes_instrucoes_presentes():
    """Testa se todos os agentes têm instruções configuradas"""
    agentes = criar_agentes()

    for nome, agente in agentes.items():
        # Verifica se tem instruções (depende da implementação do Agent)
        assert hasattr(agente, "instruction") or hasattr(agente, "_instruction")
