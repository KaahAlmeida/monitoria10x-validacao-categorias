def valida_categoria(texto, termos):
    """
    Valida categoria com até 2 termos e slop individual.
    """
    tokens = texto.lower().split()
    if len(termos) == 1:
        # 1 termo: aciona se palavra existir
        return termos[0]["palavra"].lower() in tokens

    # 2 termos
    palavra1 = termos[0]["palavra"].lower()
    palavra2 = termos[1]["palavra"].lower()
    slop1 = termos[0]["slop"]
    slop2 = termos[1]["slop"]

    # encontra todos os índices da primeira palavra
    indices1 = [i for i, t in enumerate(tokens) if t == palavra1]
    if not indices1:
        return False

    # encontra todos os índices da segunda palavra
    indices2 = [i for i, t in enumerate(tokens) if t == palavra2]
    if not indices2:
        return False

    # verifica se existe algum par de posições que respeita o slop
    for i1 in indices1:
        for i2 in indices2:
            distancia = abs(i1 - i2)
            # considera menor slop dos dois termos para essa verificação
            if distancia <= max(slop1, slop2):
                return True

    return False










