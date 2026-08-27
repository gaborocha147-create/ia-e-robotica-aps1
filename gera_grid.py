def gerar_mapa(dimensao, pct_sujeira=0.4, sujo_na_origem=False):
    total_celulas = dimensao * dimensao
    qtd_sujas = round(total_celulas * pct_sujeira)
    
    coordenadas = [(i, j) for i in range(dimensao) for j in range(dimensao)]
    
    if not sujo_na_origem:
        coordenadas.remove((0,0))
        coordenadas = min(qtd_sujas, len(coordenadas))
        
    sujas = random.sample(coordenadas, qtd_sujas)

    matriz = [['limpo' for _ in range(dimensao)] for _ in range(dimensao)]
    for (i, j) in sujas:
        matriz[i][j] = 'sujo'

    return matriz