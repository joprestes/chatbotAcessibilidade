import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from google.api_core import exceptions as google_exceptions
from chatbot_acessibilidade.core.llm_provider import GoogleGeminiClient

# Mensagem esperada
MAINTENANCE_MESSAGE = (
    "⚠️ **Sistema em Manutenção** ⚠️\n\n"
    "Nossos servidores atingiram a capacidade máxima diária. "
    "A Ada voltará a operar normalmente a partir das 06:00 a.m.\n\n"
    "*Atenciosamente, Ada Manutenção*"
)


@pytest.mark.asyncio
async def test_maintenance_message_on_double_quota_exhaustion():
    """
    Testa se a mensagem de manutenção é retornada quando ambas as chaves
    (primária e secundária) falham com erro de quota (429/ResourceExhausted).
    """
    # Mock do agente
    mock_agent = MagicMock()

    # Mock do settings para ter duas chaves
    with patch("chatbot_acessibilidade.core.llm_provider.settings") as mock_settings:
        mock_settings.google_api_key = "key1"
        mock_settings.google_api_key_second = "key2"
        mock_settings.api_timeout_seconds = 10

        client = GoogleGeminiClient(agent=mock_agent)

        # Mock do genai.Client e Runner
        with (
            patch("chatbot_acessibilidade.core.llm_provider.genai.Client"),
            patch("chatbot_acessibilidade.core.llm_provider.Runner") as mock_runner_cls,
            patch(
                "chatbot_acessibilidade.core.llm_provider.InMemorySessionService"
            ) as mock_session_cls,
        ):
            # Configura o SessionService com AsyncMock
            mock_session_instance = mock_session_cls.return_value
            mock_session_instance.create_session = AsyncMock()

            # Configura o Runner
            mock_runner_instance = mock_runner_cls.return_value

            # Simula falha na primeira tentativa (chave 1) e na segunda (chave 2)
            # O método run_async retorna um gerador assíncrono
            async def async_gen_error(*args, **kwargs):
                # Lança erro ResourceExhausted para simular quota excedida
                raise google_exceptions.ResourceExhausted("Quota exceeded")
                yield  # nunca chega aqui

            mock_runner_instance.run_async.side_effect = async_gen_error

            # Executa o método generate
            # Esperamos que ele capture os erros e retorne a mensagem de manutenção
            # em vez de lançar exceção

            # NOTA: Como ainda não implementamos, este teste deve FALHAR (lançar QuotaExhaustedError)
            try:
                response = await client.generate("Teste prompt")
                assert response == MAINTENANCE_MESSAGE
            except Exception as e:
                pytest.fail(
                    f"Deveria ter retornado mensagem de manutenção, mas lançou: {type(e).__name__}"
                )
