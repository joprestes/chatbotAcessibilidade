#!/usr/bin/env python3
"""
Script para criar GIF animado da Ada para o README
Cria uma animação suave usando os estados principais da Ada
"""

from PIL import Image
import os
import sys

# Cores para output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


def create_ada_gif():
    """Cria GIF animado da Ada com estados principais"""

    # Diretório base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "static", "images", "ada-states")
    output_path = os.path.join(base_dir, "static", "images", "ada-animated.gif")

    # Sequência de estados para a animação (ciclo suave)
    # Ordem: greeting -> idle -> surprised -> thinking -> happy -> idle -> greeting
    states = [
        "ada-greeting.png",
        "ada-idle.png",
        "ada-surprised.png",
        "ada-thinking.png",
        "ada-happy.png",
        "ada-idle.png",
        "ada-greeting.png",
    ]

    print(f"{GREEN}🎬 Criando GIF animado da Ada...{NC}")

    # Carregar imagens
    images = []
    for state in states:
        img_path = os.path.join(images_dir, state)
        if not os.path.exists(img_path):
            print(f"{YELLOW}⚠️  Imagem não encontrada: {state}{NC}")
            continue

        img = Image.open(img_path)

        # Redimensionar para 200x200 (tamanho do README)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)

        # Converter para RGBA se necessário
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        images.append(img)
        print(f"  ✓ Carregado: {state}")

    if not images:
        print(f"{YELLOW}❌ Nenhuma imagem encontrada!{NC}")
        return False

    # Criar GIF animado
    # Duração de cada frame em milissegundos
    # greeting: 800ms, idle: 600ms, surprised: 400ms, thinking: 500ms, happy: 600ms
    durations = [800, 600, 400, 500, 600, 600, 800]

    # Ajustar durações se houver menos imagens
    if len(durations) > len(images):
        durations = durations[: len(images)]
    elif len(durations) < len(images):
        # Repetir última duração
        durations.extend([durations[-1]] * (len(images) - len(durations)))

    print(f"\n{GREEN}💾 Salvando GIF...{NC}")

    # Salvar como GIF animado
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,  # Loop infinito
        optimize=True,
        quality=95,
    )

    file_size = os.path.getsize(output_path) / 1024  # KB
    print(f"\n{GREEN}✅ GIF criado com sucesso!{NC}")
    print(f"  📁 Local: {output_path}")
    print(f"  📊 Tamanho: {file_size:.1f} KB")
    print(f"  🖼️  Frames: {len(images)}")
    print(f"  ⏱️  Duração total: {sum(durations) / 1000:.1f}s")

    return True


if __name__ == "__main__":
    try:
        success = create_ada_gif()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n{YELLOW}❌ Erro ao criar GIF: {e}{NC}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
