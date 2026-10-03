# Densha de Go! 2 — validación y correcciones v0.4.17

Fecha: 2026-09-20. Base revisada: v0.4.16. Resultado: **dos encabezados defectuosos corregidos; no se detectó corrupción estructural en el alcance auditado**. La traducción completa del juego sigue abierta.

## Hallazgo y reparación

Al perder una partida de Kanku y dejar terminar la cuenta de continuación, la línea sobre GAME OVER mostraba letras fragmentadas. El volcado de memoria coincidía con el recurso comprimido: el defecto estaba en los gráficos ingleses heredados, no en una descompresión fallida. El encabezado equivalente de finalización tenía el mismo problema.

| Original | Inglés conservado y reparado | Recurso | Validación |
|---|---|---|---|
| 運転中止 | RUN ABORTED | 0x3D63E8 | Partida y derrota con botones; pantalla real en Mesen |
| 運転終了 | RUN ENDED | 0x3D61C0 | Consumidor real, mediante transición asistida al subestado 0x88 |

Se redibujaron los primeros 24 tiles de cada atlas con glifos 5×7 coherentes y la paleta del consumidor. Los otros 48 tiles de cada recurso, incluido GAME OVER, permanecen idénticos. Los flujos resultantes ocupan 533/543 y 518/550 bytes de su capacidad original, respectivamente. Cambian 953 bytes respecto a v0.4.16, exclusivamente en ambos flujos y el checksum. No cambió el código del juego.

Evidencia: `evidence/V0417_BEFORE_AFTER.png`, `reports/BUILD_VALIDATION.json` y los directorios `gameover_*` / `ended_*` de `evidence/runtime`.

## Cursos: corrección de la clasificación anterior

**Los seis cursos ya están disponibles por navegación normal.** Derecha abre la segunda página del selector; izquierda regresa a la primera. No fue necesario modificar la ROM, inyectar un índice de curso ni completar partidas para abrirla. La rutina de navegación coincide byte por byte con la japonesa.

| Página | Curso mostrado | Modalidad |
|---|---|---|
| 1 | Hokuhoku Line | Rapid / Easy |
| 1 | Akita Shinkansen | Komachi / Normal |
| 1 | Keihin-Tohoku | Rapid / Normal |
| 2 | Osaka Loop | Local / Normal |
| 2 | Akita Shinkansen | Komachi / Hard |
| 2 | Osaka Loop | Kanku Rapid / Hard |

Se recorrieron las dos páginas con botones tanto en la original como en v0.4.16, y se arrancaron las tres opciones de la segunda página verificando el índice realmente seleccionado. Esta evidencia sigue aplicando a v0.4.17: la navegación y el código permanecen intactos. Kanku se volvió a probar en v0.4.17 hasta GAME OVER.

Atención para herramientas: el juego intercambia los índices 2 y 3 después de confirmar la selección. No confundir índice del selector con índice interno durante la partida. Los dos primeros intentos automatizados pulsaban derecha demasiado pronto: sus resultados se conservan, pero se excluyen como evidencia de Osaka Local/Akita Hard. Las repeticiones `*_verified` sí comprobaron el curso.

Quedan pendientes las escenas/variantes finales dependientes del rendimiento. El código de F000:373A comprueba 0x078F y los contadores 0x077F–0x0781; todavía no se atribuye un significado completo a esas condiciones. Esto es distinto del acceso a los seis cursos.

## Integridad y pruebas

- ROM de 4.194.304 bytes; checksum almacenado y calculado: **0x5C91**. Cabecera restante sin cambios frente a la original.
- 60 tablas coherentes, 3.159 descriptores únicos y 3.121 flujos comprimidos comprobados. Sin cambios de tamaño descomprimido, invasión de la siguiente asignación, tokens que excedan la longitud de salida ni referencias de distancia cero. Los recursos no comprimidos se mantienen inventariados, sin fingir que todos sus formatos están interpretados.
- Los cuatro parches generados —BPS e IPS, acumulativos e incrementales— reconstruyen exactamente v0.4.17. El constructor también reproduce la ROM en un directorio limpio, con `python3 -S`, sin paquetes externos ni ROM intermedia.
- 74 capturas comparadas con v0.4.16: 69 idénticas y 5 con diferencias limitadas al rectángulo de los encabezados reparados. Sin cambios fuera de ese rectángulo.
- Pruebas acotadas a 85 s internos / 90 s de supervisor. La corrida Hokuhoku de 45.000 frames, con el temporizador congelado, alcanzó los créditos sin nuevas diferencias visuales en las capturas comparables. No alcanzó RUN ENDED dentro del límite; se pasó a la comprobación asistida de su consumidor.
- RUN ENDED se cargó desde 0x3D61C0 a WRAM 0x2CC0 a través de su rutina real. La prueba inyectó únicamente el subestado 0x88 desde el selector: **no acredita finalización natural**. RUN ABORTED se cargó a WRAM 0x2E40 sin inyección ni congelación.

Estas pruebas no equivalen a recorrer todos los finales, avisos y combinaciones de juego. Los registros de lecturas no inicializadas de arranque D0–DF también aparecen en la original; no se atribuyen a esta corrección.

## Texto ambiental y traducciones pendientes

Se extrajeron **2.915 recursos ambientales** de los bancos 03–3C. Los bancos completos son idénticos a la japonesa, y cada recurso descomprimido conserva su contenido. Se generó una galería navegable: `evidence/environment_audit/ENVIRONMENT_CATALOG.html`.

Se inspeccionaron visualmente **204 recursos únicos**: una muestra de cada banco y las secuencias completas de los bancos 03, 36 y 37. **2.711 recursos aún no tienen revisión visual individual**. Estos números cuentan gráficos, no textos ni porcentaje de traducción.

Se vincularon 143 recursos ambientales al consumidor E000:C186 en una partida de Osaka Local. Su secuencia de primera utilización coincide con el prefijo de la original. Se observaron diferencias leves de momento de carga: en una de diez regiones de captura comparadas hubo 208 píxeles distintos, sin modificación del recurso subyacente. No se afirma equivalencia de cada frame entre JP e inglés.

Pendientes concretos:

1. Posibles rótulos/anuncios diminutos de fachadas y andenes; requieren lectura fiable, contexto y seguimiento de sus variantes en perspectiva. Los píxeles ambiguos no se registraron como japonés confirmado.
2. Destinos/rótulos incluidos en cinco fotografías de trenes del banco 02.
3. Variantes de bonus/acople y avisos poco frecuentes todavía no comprobados en su contexto.
4. Terminología y abreviaturas, incluida AKITA SHINKAN, visible en el selector.
5. Acceso natural a RUN ENDED y ramas de finalización por rendimiento.

No se obtuvo una transcripción japonesa ambiental nueva con confianza suficiente para sustituirla. Los dos cambios de esta versión reparan traducciones inglesas ya integradas. No se declara “cero japonés pendiente” ni traducción terminada.

## Reproducción y entrega

Aplicar `patches/Densha_de_Go_2_EN_v0.4.17_CUMULATIVE.bps` a la original japonesa identificada abajo. Para partir de v0.4.16 usar el BPS incremental correspondiente. El paquete contiene fuentes acumulativas, ROMs de referencia, historial, parches, inventarios, capturas y scripts.

Constructor: `python3 tools/build.py` o `BUILD_WINDOWS.bat`. La prueba se realizó en Linux; el archivo BAT es un envoltorio de Python y no se ejecutó en Windows. El constructor usa únicamente la biblioteca estándar; los exportadores visuales opcionales usan NumPy y Pillow.

- Original SHA-256: `3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29`
- v0.4.17 SHA-256: `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513`
- BPS acumulativo SHA-256: `c74d4d4dd1f72a23a791c0320e456b3d3a8b2aa0ce5a95d01c6a0385c0229c21`

`reports/QA_SUMMARY.json` delimita los cierres y pendientes; `NEXT_STAGE.md` permite continuar sin repetir los hallazgos ya resueltos.
