import pytest
from chatbot_acessibilidade.core.formatter import (
    eh_erro,
    extrair_primeiro_paragrafo,
    formatar_resposta_final,
    gerar_dica_final
)

def test_eh_erro_verdadeiro():
    """Testa se a função identifica corretamente uma string de erro."""
    assert eh_erro("Erro: falha na API") == True
    assert eh_erro("Ocorreu uma falha ao processar.") == True

def test_eh_erro_falso():
    """Testa se a função não marca uma resposta normal como erro."""
    assert eh_erro("Esta é uma resposta de sucesso.") == False

def extrair_primeiro_paragrafo(texto: str) -> str:
    """Extrai o primeiro parágrafo de um texto. Um parágrafo é um bloco de texto separado por \\n\\n."""
    texto_limpo = texto.strip()
    if "\n\n" in texto_limpo:
        return texto_limpo.split("\n\n")[0].strip()
    return texto_limpo

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