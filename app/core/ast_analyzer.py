"""
Módulo centralizado de análisis AST.
Todas las features que necesiten inspeccionar código Python sin ejecutarlo
deben importar desde aquí para reutilizar el parse y evitar duplicación.
"""
import ast


def _safe_parse(code: str) -> ast.Module | None:
    """Parsea el código y retorna el árbol AST. Retorna None si hay SyntaxError."""
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


# ── Funciones definidas ────────────────────────────────────────────────────────

def get_defined_functions(code: str) -> set[str]:
    """Retorna los nombres de todas las funciones definidas en el código (def)."""
    tree = _safe_parse(code)
    if not tree:
        return set()
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def check_required_functions(code: str, required: list[str]) -> str | None:
    """
    Verifica que el código defina todas las funciones de la lista `required`.
    Retorna un mensaje de error si falta alguna, None si todas están presentes.
    """
    if not required:
        return None
    defined = get_defined_functions(code)
    missing = [f for f in required if f not in defined]
    if missing:
        names = ", ".join(f"`{f}`" for f in missing)
        return f"Tu código debe definir la(s) función(es): {names}"
    return None


# ── Detección de conceptos (para Logros ocultos y Analítica) ───────────────────

def detect_concepts(code: str) -> list[str]:
    """
    Detecta conceptos Python presentes en el código.
    Usado por: Logros ocultos del Sandbox, Mapa de calor de errores.
    """
    tree = _safe_parse(code)
    if not tree:
        return []

    concepts = []
    nodes = list(ast.walk(tree))
    node_types = {type(n) for n in nodes}

    if ast.For in node_types:
        concepts.append("loop_for")
    if ast.While in node_types:
        concepts.append("loop_while")
    if ast.Try in node_types:
        concepts.append("try_except")
    if ast.ListComp in node_types:
        concepts.append("list_comp")
    if ast.Lambda in node_types:
        concepts.append("lambda")
    if ast.ClassDef in node_types:
        concepts.append("class")
    if ast.DictComp in node_types:
        concepts.append("dict_comp")
    if ast.GeneratorExp in node_types:
        concepts.append("generator")

    # Bucle anidado: For/While que contiene otro For/While
    for node in nodes:
        if isinstance(node, (ast.For, ast.While)):
            inner = list(ast.walk(node))
            if any(isinstance(n, (ast.For, ast.While)) for n in inner[1:]):
                concepts.append("nested_loop")
                break

    # Recursión: FunctionDef que contiene una Call a sí misma
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
            for call in calls:
                if isinstance(call.func, ast.Name) and call.func.id == node.name:
                    concepts.append("recursion")
                    break

    # Decorator: FunctionDef con al menos un decorator
    for node in nodes:
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            concepts.append("decorator")
            break

    return list(set(concepts))