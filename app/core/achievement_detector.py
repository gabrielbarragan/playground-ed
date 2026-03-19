"""
Bridge entre detect_concepts (ast_analyzer) y el sistema de logros.
Recibe código y retorna los trigger_values de SandboxAchievement que coinciden.
"""
from app.core.ast_analyzer import detect_concepts


def get_triggered_values(code: str) -> list[str]:
    """
    Retorna lista de trigger_values presentes en el código.
    Incluye triggers simples (slugs individuales) y combos ("a+b").
    """
    concepts = set(detect_concepts(code))
    triggered: list[str] = list(concepts)

    # Combos: todos los pares posibles de conceptos detectados
    # Solo los que el sistema haya definido en BD se crearán como logros.
    # Aquí generamos todas las combinaciones para que la query en BD los filtre.
    concepts_list = sorted(concepts)
    for i, a in enumerate(concepts_list):
        for b in concepts_list[i + 1:]:
            triggered.append(f"{a}+{b}")

    return triggered