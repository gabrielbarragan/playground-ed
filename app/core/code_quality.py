def count_effective_lines(code: str) -> int:
    """
    Cuenta líneas de código efectivo.
    Excluye líneas vacías y líneas que son únicamente comentarios (#).
    """
    return sum(
        1 for line in code.splitlines()
        if line.strip() and not line.strip().startswith('#')
    )


def calculate_lines_bonus(code: str, min_lines: int, max_lines: int, bonus_points: int) -> int:
    """
    Retorna bonus_points si el código efectivo está dentro del rango [min_lines, max_lines].
    Retorna 0 si está fuera del rango.
    """
    effective = count_effective_lines(code)
    if min_lines <= effective <= max_lines:
        return bonus_points
    return 0