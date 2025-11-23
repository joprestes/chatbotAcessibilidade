import webbrowser
import os
import sys
from pathlib import Path

# Adiciona src ao path para imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def pytest_sessionfinish(session):
    """
    Este hook é chamado após toda a sessão de testes terminar.
    Ele verifica se um relatório HTML foi gerado e tenta abri-lo.
    """
    # A opção --html salva o caminho do relatório em session.config.option.htmlpath
    # Usamos getattr para evitar um erro caso a opção --html não seja usada.
    html_report_path = getattr(session.config.option, 'htmlpath', None)

    if html_report_path:
        # Constrói o caminho absoluto para o arquivo (melhor para webbrowser)
        absolute_html_path = os.path.abspath(html_report_path)
        print(f"\nFim da sessão de testes. Tentando abrir o relatório HTML: {absolute_html_path}")
        try:
            # file_uri garante que funcione bem em diferentes sistemas, especialmente no Windows
            file_uri = f"file://{absolute_html_path}"
            webbrowser.open_new_tab(file_uri)
            print(f"Relatório solicitado para abertura em: {file_uri}")
        except Exception as e:
            print(f"Não foi possível abrir o relatório HTML no navegador: {e}")
    else:
        print("\nFim da sessão de testes. Nenhum caminho de relatório HTML configurado para abrir.")