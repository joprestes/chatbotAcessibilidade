import pytest

pytestmark = pytest.mark.unit

from chatbot_acessibilidade.core.formatter import (
    eh_erro,
    extrair_primeiro_paragrafo,
    formatar_resposta_final,
    gerar_dica_final,
)


def test_eh_erro_verdadeiro():
    """Testa se a função identifica corretamente uma string de erro."""
    assert eh_erro("Erro: falha na API")
    assert eh_erro("Ocorreu uma falha ao processar.")


def test_eh_erro_falso():
    """Testa se a função não marca uma resposta normal como erro."""
    assert not eh_erro("Esta é uma resposta de sucesso.")


def test_extrair_paragrafo_texto_curto():
    """Testa o fallback para textos sem quebra de parágrafo."""
    texto = "Um texto curto sem quebras."
    assert extrair_primeiro_paragrafo(texto) == "Um texto curto sem quebras."


def test_formatar_resposta_final_retorna_dicionario():
    """Testa se a função retorna um dicionário com as chaves corretas."""
    resposta = formatar_resposta_final("intro", "conceitos", "testes", "aprofundar", "dica")

    assert isinstance(resposta, dict)
    assert "📘 **Introdução**" in resposta
    assert "🧪 **Como Testar na Prática**" in resposta
    assert resposta["👋 **Dica Final**"] == "dica"


def test_gerar_dica_final_especifica():
    """Testa se gera dicas específicas baseadas na pergunta."""
    # Testa a dica de teclado
    pergunta_teclado = "como usar o teclado?"
    dica_teclado = gerar_dica_final(pergunta_teclado, "")
    assert "teclado" in dica_teclado.lower()

    # Testa a dica de contraste
    pergunta_contraste = "fale sobre contraste de cores"
    dica_contraste = gerar_dica_final(pergunta_contraste, "")
    assert "contraste" in dica_contraste.lower()

    # Testa a dica de leitor de tela
    pergunta_leitor = "como testar com leitor de tela"
    dica_leitor = gerar_dica_final(pergunta_leitor, "")
    assert "leitores de tela" in dica_leitor.lower()


def test_gerar_dica_final_generica():
    """Testa se gera uma dica genérica quando não há palavra-chave."""
    assert "processo contínuo" in gerar_dica_final("o que é acessibilidade?", "")


def test_extrair_primeiro_paragrafo_com_multiplos_paragrafos():
    """Testa extração do primeiro parágrafo quando há múltiplos."""
    texto = (
        "Primeiro parágrafo com mais de 30 caracteres.\n\nSegundo parágrafo.\n\nTerceiro parágrafo."
    )
    resultado = extrair_primeiro_paragrafo(texto)
    assert resultado == "Primeiro parágrafo com mais de 30 caracteres."


def test_extrair_primeiro_paragrafo_texto_curto_sem_ponto():
    """Testa fallback para texto curto sem ponto final."""
    texto = "Texto curto sem ponto final"
    resultado = extrair_primeiro_paragrafo(texto)
    assert len(resultado) <= 303  # 300 + "..."
    assert "..." in resultado or resultado.endswith(".")


def test_extrair_primeiro_paragrafo_texto_longo_sem_paragrafos():
    """Testa extração de texto longo sem quebras de parágrafo."""
    texto = "Este é um texto longo sem quebras de parágrafo. " * 10
    resultado = extrair_primeiro_paragrafo(texto)
    # O resultado pode ser maior que 303 se não houver ponto antes de 300 caracteres
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_eh_erro_case_insensitive():
    """Testa se eh_erro funciona com diferentes casos."""
    assert eh_erro("ERRO: algo deu errado")
    assert eh_erro("FALHA na execução")
    assert eh_erro("ErRo: teste")


def test_formatar_resposta_final_com_espacos():
    """Testa se formatar_resposta_final remove espaços extras."""
    resposta = formatar_resposta_final(
        "  intro  ", "  conceitos  ", "  testes  ", "  aprofundar  ", "  dica  "
    )
    assert resposta["📘 **Introdução**"] == "intro"
    assert resposta["🔍 **Conceitos Essenciais**"] == "conceitos"
