"""
Configuração do mutmut para mutation testing

Este arquivo configura quais arquivos devem ser mutados e quais testes executar.
"""

def pre_mutation(context):
    """
    Hook executado antes de cada mutação.
    Pode ser usado para pular certas mutações.
    """
    # Pula mutações em linhas de import
    if context.current_source_line.strip().startswith('import '):
        context.skip = True
    if context.current_source_line.strip().startswith('from '):
        context.skip = True
