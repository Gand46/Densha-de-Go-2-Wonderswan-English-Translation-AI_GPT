# Densha de Go! 2 v0.4.17 — acceso sintético dirigido

Build evaluada: `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513` (SHA-256). Mesen 2.1.1 Linux x64: `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`. No hubo cambios en la ROM ni en el BPS acumulativo de v0.4.17.

`qa/synthetic_v0417/RESULTS.json` contiene 24 filas de alcance: **16 `PASS_SYNTHETIC` de consumidor**, 2 `PASS_SCRIPTED_NATURAL` y 6 puntos sin aprobación. Cada aprobación sintética tiene `RUN.json`, `REVIEW.json`, `REVIEW_RESULT.json`, traza, captura y hash. `ws_review.py` del kit v1.2 comprobó procedencia y controles de consumidor; la revisión visual se hizo aparte y no se infiere automáticamente del JSON.

| Familia | Resultado | Intervención y evidencia |
|---|---|---|
| RUN ENDED y cinco rutas de F000:373A | 6 `PASS_SYNTHETIC` de consumidor | En el selector se escribió el subestado `0x0395=0x88`; las rutas añadieron `0x078F`, `0x077F–0x0781` y `0x019C` antes de la ejecución. El juego cargó `0x3D61C0` a `0x2CC0` y dibujó RUN ENDED. Las rutas con umbral alto mostraron las dos figuras previstas. |
| BONUS | `PASS_SYNTHETIC` de consumidor | Con el curso Osaka Local activo, un único bit en `0x0379` llevó a F000:794C. El juego cargó `0x3D92E1` a `0x2780` y mostró BONUS con puntuación. |
| PENALTY! | `PASS_SYNTHETIC` de consumidor | Se creó en un slot vacío de WRAM un objeto de actualización 07 con contador `0x25`. F000:660B→6636 cargó `0x3D93AB` a `0x2780` y se capturó PENALTY! con descuento. Revisar todavía su contraste frente a la vía a escala nativa. |
| STOP STATION PASSED y ATS ACTUATED | 2 `PASS_SCRIPTED_NATURAL` | Aparecieron con botones en Osaka Local sin inyección; sus cargas reales fueron `0x3D8DD2` y `0x3D855C`. |
| Otros ocho avisos | 8 `PASS_SYNTHETIC` de consumidor | Al prepararse STOP STATION PASSED, se sustituyó **solo** el puntero de descriptor `0x0A14` en WRAM, con guardas de banco, destino y valor previo. El consumidor real cargó y mostró cada aviso sin modificar la ROM. Se probaron HARD BRAKING, BUFFER STOP COLLISION, MOVE THE TRAIN, SIGN IGNORED, CAB SIGNAL IGNORED, SPEED LIMIT EXCEEDED, TIME UP y DEPART REQUIRED. |

## Límites y hallazgos pendientes

- El `PASS_SYNTHETIC` se refiere al **consumidor y recurso identificado**. No demuestra que todas las condiciones reales del juego activen esas ramas ni concede aprobación global de traducción, tipografía o RC.
- El globo de diálogo de la rama intermedia del final aparece vacío tanto en inglés como en japonés al entrar desde el selector. Por ello pasan el consumidor y el encabezado, **no** el diálogo contextual.
- Un ensayo para el descriptor adicional `0x3D90C0` terminó por límite del emulador en dos intentos y no generó captura o traza. Estado: `NOT_VALIDATED`. Ese ensayo no permite atribuir corrupción a la ROM.
- El minijuego de **PASS RANGE / DANGER** no se alcanzó en las pruebas acotadas de Osaka Local, Kanku ni Akita. Sus recursos de banco 02, índices 91–96, no se aprobaron por su sola presencia estática. Requiere localizar su estado/consumidor y hacer una inyección con precondiciones y captura.
- Las fotografías de trenes, rótulos ambientales diminutos, terminología y ledger histórico siguen en revisión separada. Los seis cursos ya eran accesibles con botones; la terminación natural completa no es una condición para los `PASS_SYNTHETIC` anteriores.

## Reproducción dirigida

Partir de la ROM japonesa identificada en `project.json`. Construir con `python3 tools/build.py /ruta/ROM_JP.ws`. Usar Mesen 2.1.1 Linux x64 con Lua I/O habilitado; pasar el ejecutable por `--mesen`. El runner usa un nombre de salida nuevo por ejecución y límites 85/90 s. Ejemplos:

```sh
END_CASE=high_zero_a python3 tools/run_mesen.py --mesen /ruta/Mesen --name end_high_a --mode idle --frames 1300 --lua qa/scripts/synthetic_v0417/end_branches.lua
NOTICE_DESCRIPTOR=866D python3 tools/run_mesen.py --mesen /ruta/Mesen --name hard_braking --mode course --index 3 --frames 6800 --lua qa/scripts/synthetic_v0417/notice_substitute.lua
python3 tools/run_mesen.py --mesen /ruta/Mesen --name bonus --mode course --index 3 --frames 3200 --lua qa/scripts/synthetic_v0417/bonus_trigger.lua
python3 tools/run_mesen.py --mesen /ruta/Mesen --name penalty --mode course --index 3 --frames 3250 --lua qa/scripts/synthetic_v0417/penalty_object.lua
```

`END_CASE`: `low`, `middle`, `high_nonzero`, `high_zero_a`, `high_zero_b`. Descriptores comprobados por sustitución: `866D`, `8757`, `887F`, `8A60`, `8B54`, `8C9D`, `8463`, `8FD9`. El script verifica que el origen sea `8DD0`, el banco 3D y el destino `0x2580` antes de escribir; un cambio en la revisión de ROM exige nuevos guards. Las capturas conservan píxeles nativos 224×157. Un `exit_code=0` sin traza y captura del recurso correspondiente no basta para marcar PASS.

La matriz evita repetir partidas extensas. El siguiente trabajo concreto es una entrada sintética al consumidor del acople, el control del descriptor `0x3D90C0` y la revisión lingüística/visual independiente. Hasta cerrar los controles globales, la etiqueta sigue siendo `v0.4.17-test`.
