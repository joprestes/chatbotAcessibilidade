#!/bin/bash

echo "🛠️ Criando ambiente virtual '.venv' com Python 3..."
python3 -m venv .venv

echo "✅ Ativando virtualenv..."
source .venv/bin/activate

echo "📦 Instalando dependências do requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Pronto! Execute com: source .venv/bin/activate && streamlit run app.py"
