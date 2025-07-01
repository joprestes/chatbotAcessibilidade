# chatbot_acessibilidade/utils.py
def eh_erro(texto: str) -> bool:
    return texto.startswith("Erro") or "falha" in texto.lower()

def gerar_dica_final(pergunta: str, resposta: str) -> str:
    p = pergunta.lower()
    if "teclado" in p:
        return "Verifique se é possível navegar usando apenas o teclado..."
    if "contraste" in p:
        return "Use ferramentas como WebAIM ou axe para validar o contraste..."
    if "leitor de tela" in p:
        return "Use o NVDA ou VoiceOver para testar a leitura de tela."
    return "A acessibilidade é um processo contínuo. Teste, colete feedback real e melhore sempre."

def formatar_resposta_final(resumo: str, conceitos: str, testes: str, aprofundar: str, dica: str) -> str:
    return f"""
📘 **Introdução**  
{resumo.strip()}

---

🔍 **Conceitos Essenciais**  
{conceitos.strip()}

---

🧪 **Como Testar na Prática**  
{testes.strip()}

---

📚 **Quer se Aprofundar?**  
{aprofundar.strip()}

---

👋 **Dica Final**  
{dica.strip()}
""".strip()

def extrair_primeiro_paragrafo(texto: str) -> str:
    paragrafos = [p.strip() for p in texto.split("\n\n") if len(p.strip()) > 30]
    if paragrafos:
        return paragrafos[0]
    return texto[:300].rsplit('.', 1)[0] + '.' if '.' in texto[:300] else texto[:300] + "..."
