import time
import numpy as np
from multiprocessing import Pipe, Process


def reparto_filas(N, n_proc, rank):
    """Devuelve (fila_inicial, num_filas) del proceso `rank`.
    CORRECCIÓN: las N % n_proc filas sobrantes se reparten entre los primeros procesos."""
    base, resto = divmod(N, n_proc)
    filas = base + (1 if rank < resto else 0)
    inicio = rank * base + min(rank, resto)
    return inicio, filas


# Asignación de cada proceso en una franja del dominio global
def inicializacion_subdominio(n_proc, N, pert=1.01, rank=0, g=1, franja=None):
    """Crea la matriz local del proceso `rank` con g filas fantasma arriba y abajo y una
    columna fantasma a cada lado. `franja` = (inicio, filas) permite un reparto distinto
    al uniforme (se usa en el balanceo de carga)."""
    inicio, subgrid_rows = franja if franja else reparto_filas(N, n_proc, rank)
    cols = N
    # Matriz local con bordes extra (ghost cells)
    grid = np.zeros((subgrid_rows + 2 * g, cols + 2), dtype=np.float64)
    # Perturbación inicial centrada en (50, 50)
    # CORRECCIÓN: la fila global depende de la posición del proceso (inicio + r)
    # CORRECCIÓN: vectorizado y escrito en las columnas reales 1..cols
    gr = inicio + np.arange(subgrid_rows)[:, None]
    c = np.arange(cols)[None, :]
    dist = np.sqrt((gr - 50) ** 2 + (c - 50) ** 2)
    grid[g:g + subgrid_rows, 1:cols + 1] = 100 * pert * np.exp(-dist / 120)
    return grid, subgrid_rows, cols
# Intercambio de bordes con los vecinos del Norte (arriba) y del Sur (abajo)
def intercambio_ghost_cells(grid, subgrid_rows, pipe_top, pipe_bottom, g=1, rank=0):
    """Envía las g filas frontera propias y recibe las g filas fantasma de cada vecino.
    Devuelve (bytes_enviados, mensajes)."""
    h = subgrid_rows
    enviados = mensajes = 0
    # CORRECCIÓN: orden par/impar para evitar interbloqueo con mensajes grandes.
    # Fase A: parejas (0,1), (2,3)...  Fase B: parejas (1,2), (3,4)...
    lados = ("sur", "norte") if rank % 2 == 0 else ("norte", "sur")
    for lado in lados:
        conn = pipe_bottom if lado == "sur" else pipe_top
        if conn is None:
            continue
        if lado == "sur":       # mis últimas g filas → vecino del Sur
            borde = grid[h:h + g, :].copy()
            conn.send(borde)                   # el de arriba de la pareja envía primero
            grid[h + g:h + 2 * g, :] = conn.recv()
        else:                   # mis primeras g filas → vecino del Norte
            borde = grid[g:2 * g, :].copy()
            recibido = conn.recv()             # el de abajo de la pareja recibe primero
            conn.send(borde)
            grid[0:g, :] = recibido
        enviados += borde.nbytes
        mensajes += 1
    return enviados, mensajes


def aplicar_fronteras(grid, subgrid_rows, es_borde_norte, es_borde_sur, g=1):
    """Modificación de condiciones físicas en los bordes del dominio GLOBAL.
    CORRECCIÓN: el original hacía `grid[0,0] = grid[1,:]` (ValueError) y solo cuando SÍ
    había vecino. La frontera se aplica cuando NO hay vecino: la fila fantasma copia a la
    fila real (flujo cero a través del borde)."""
    if es_borde_norte:
        grid[g - 1, :] = grid[g, :]
    if es_borde_sur:
        grid[g + subgrid_rows, :] = grid[g + subgrid_rows - 1, :]
# Actualización de las temperaturas/presión atmosférica
def calcular_paso_atmosferico(grid, f0, f1, cols, tormenta=None, sub_pasos=1):
    """Calcula el paso t+1 de las filas locales [f0, f1) con el esténcil de 5 puntos.
    El original actualizaba siempre las filas 1..subgrid_rows; aquí el rango se recibe
    como parámetro para soportar franjas de ghost cells de ancho g."""
    grid_next = grid.copy()
    # CORRECCIÓN: las cuatro rebanadas deben tener (f1-f0) x cols elementos
    grid_next[f0:f1, 1:cols + 1] = 0.25 * (
        grid[f0 - 1:f1 - 1, 1:cols + 1] +   # vecino del Norte
        grid[f0 + 1:f1 + 1, 1:cols + 1] +   # vecino del Sur
        grid[f0:f1, 0:cols] +               # vecino del Oeste
        grid[f0:f1, 2:cols + 2]             # vecino del Este
    )
    # Tormenta: convección resuelta con sub-iteraciones solo en las celdas afectadas
    if tormenta is not None and sub_pasos > 1:
        m = tormenta[f0:f1]
        if m.any():
            filas = np.nonzero(m.any(axis=1))[0]
            a, b = f0 + filas[0], f0 + filas[-1] + 1
            zona = grid_next[a:b, 1:cols + 1]
            mz = tormenta[a:b]
            for _ in range(sub_pasos - 1):
                zona = np.where(mz, zona + 1e-4 * np.sin(zona) * np.exp(-zona / 200), zona)
            grid_next[a:b, 1:cols + 1] = zona
    return grid_next
# Ciclo principal SPMD que orquesta comunicación y cómputo
def worker_spmd(num_proc, N, steps, pipe_top, pipe_bottom, result_pipe, pertubacion=1.01,
                rank=0, g=1, tormenta_global=None, sub_pasos=1, franjas=None,
                guardar_historico=False):
    franja = franjas[rank] if franjas else None
    grid, subgrid_rows, cols = inicializacion_subdominio(num_proc, N, pertubacion, rank, g,
                                                         franja)
    inicio = franja[0] if franja else reparto_filas(N, num_proc, rank)[0]
    h, H = subgrid_rows, subgrid_rows + 2 * g
    assert h >= g, "cada franja necesita al menos g filas propias"
    norte, sur = pipe_top is None, pipe_bottom is None     # ¿borde del dominio global?

    # Máscara local de tormenta (con las mismas filas fantasma que grid)
    tormenta = None
    if tormenta_global is not None:
        tormenta = np.zeros((H, cols), dtype=bool)
        a, b = max(inicio - g, 0), min(inicio + h + g, N)
        tormenta[a - (inicio - g):b - (inicio - g)] = tormenta_global[a:b]

    historico, muestreo = [], (steps // 10 if steps > 10 else 1)
    t_comp = t_com = 0.0
    enviados = mensajes = 0
    step = 0
    while step < steps:
        # Comunicación de bordes (cada g pasos)
        t0 = time.perf_counter()
        b, m = intercambio_ghost_cells(grid, h, pipe_top, pipe_bottom, g, rank)
        enviados += b; mensajes += m
        t_com += time.perf_counter() - t0
        # Cómputo numérico: hasta g pasos con la zona válida encogiéndose
        t0 = time.perf_counter()
        for s in range(1, min(g, steps - step) + 1):
            aplicar_fronteras(grid, h, norte, sur, g)
            f0 = g if norte else s
            f1 = g + h if sur else H - s
            grid = calcular_paso_atmosferico(grid, f0, f1, cols, tormenta, sub_pasos)
            # Muestreo periódico para visualización del fenómeno atmosférico
            if guardar_historico and step % muestreo == 0:
                # CORRECCIÓN: append recibe una tupla (paso, campo)
                historico.append((step, grid[g:g + h, 1:cols + 1].copy()))
            step += 1
        t_comp += time.perf_counter() - t0

    resultado = {"rank": rank, "final": grid[g:g + h, 1:cols + 1].copy(),
                 "historico": historico, "t_comp": t_comp, "t_com": t_com,
                 "bytes": enviados, "mensajes": mensajes}
    if result_pipe is None:          # ejecución secuencial en el proceso principal
        return resultado
    # Enviar el registro histórico y las métricas al proceso principal
    result_pipe.send(resultado)
    result_pipe.close()
def ejecutar_simulacion(num_proc, N, steps, g=1, pertubacion=1.01, zona_tormenta=None,
                        sub_pasos=1, franjas=None, guardar_historico=False):
    """Ejecuta la simulación con num_proc procesos. Devuelve (malla_final, métricas, historico).
    zona_tormenta = (fila0, fila1, col0, col1) en fracciones de N."""
    t_inicio = time.perf_counter()
    tormenta = None
    if zona_tormenta is not None:
        tormenta = np.zeros((N, N), dtype=bool)
        f0, f1, c0, c1 = (int(round(z * N)) for z in zona_tormenta)
        tormenta[f0:f1, c0:c1] = True
    if franjas is not None:
        num_proc = len(franjas)
    args = dict(pertubacion=pertubacion, g=g, tormenta_global=tormenta,
                sub_pasos=sub_pasos, franjas=franjas, guardar_historico=guardar_historico)

    if num_proc == 1:
        res = [worker_spmd(1, N, steps, None, None, None, rank=0, **args)]
    else:
        vecinos = [Pipe() for _ in range(num_proc - 1)]          # (i) ↔ (i+1)
        al_maestro = [Pipe(duplex=False) for _ in range(num_proc)]
        procesos = []
        for r in range(num_proc):
            top = vecinos[r - 1][1] if r > 0 else None
            bottom = vecinos[r][0] if r < num_proc - 1 else None
            pr = Process(target=worker_spmd, args=(num_proc, N, steps, top, bottom,
                                                   al_maestro[r][1]),
                         kwargs=dict(rank=r, **args))
            pr.start()
            procesos.append(pr)
        res = [al_maestro[r][0].recv() for r in range(num_proc)]
        for pr in procesos:
            pr.join()

    res.sort(key=lambda x: x["rank"])
    malla = np.vstack([x["final"] for x in res])
    historico = None
    if guardar_historico:
        historico = [(paso, np.vstack([x["historico"][i][1] for x in res]))
                     for i, (paso, _) in enumerate(res[0]["historico"])]
    metricas = {"t_total": time.perf_counter() - t_inicio,
                "por_proceso": [{k: x[k] for k in ("t_comp", "t_com", "bytes", "mensajes")}
                                for x in res]}
    return malla, metricas, historico


def particion_por_costo(N, n_proc, zona_tormenta, peso_tormenta):
    """Reparto BALANCEADO: cortes que igualan el costo de cada proceso.
    peso_tormenta = costo EXTRA de una celda de tormenta, en unidades del costo de una
    celda normal (se obtiene midiendo una corrida, como haría un balanceador dinámico)."""
    tormenta = np.zeros((N, N), dtype=bool)
    f0, f1, c0, c1 = (int(round(z * N)) for z in zona_tormenta)
    tormenta[f0:f1, c0:c1] = True
    costo_fila = N + tormenta.sum(axis=1) * peso_tormenta
    acum = np.concatenate([[0], np.cumsum(costo_fila)])
    cortes = np.searchsorted(acum, np.linspace(0, acum[-1], n_proc + 1)).clip(0, N)
    cortes[0], cortes[-1] = 0, N
    for i in range(1, n_proc):
        cortes[i] = max(cortes[i], cortes[i - 1] + 1)
    return [(int(cortes[i]), int(cortes[i + 1] - cortes[i])) for i in range(n_proc)]
