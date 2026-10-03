# Densha de Go! 2 v0.4.17 — revisión rápida previa al primer RC

**Resultado:** las comprobaciones técnicas y las transiciones breves ensayadas pasan. La ROM sigue siendo v0.4.17, con SHA-256 `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513`. Esta entrega es un checkpoint de validación, no un RC declarado ni una nueva versión de ROM.

Las tres pruebas nuevas de Mesen sumaron **35,334 segundos de ejecución**. La inspección estática del paquete y su reconstrucción tardaron aproximadamente 3 segundos por corrida. El análisis de resultados se realizó aparte; no se necesitaron horas de juego.

| Validación adicional | Resultado y alcance |
|---|---|
| Integridad del ZIP realmente entregado | CRC correcto; verificados los hashes de sus 3.864 archivos declarados en el manifiesto |
| Construcción desde extracción limpia | ROM idéntica; Python estándar con `-S`; sin ROM intermedia; ruta con espacios y ñ |
| Reproducibilidad de parches | BPS e IPS, acumulativo e incremental: cuatro archivos idénticos a los entregados y aplicación exacta |
| Entradas incorrectas | BPS rechaza ROM de origen incorrecta, parche alterado y parche truncado |
| Tablas y formatos | 60 tablas de punteros y 3.159 etiquetas de descriptor idénticas a la japonesa; sin cambios en asignaciones no comprimidas |
| Opciones | 15 capturas idénticas a la referencia v0.4.16: dificultad, controles, distancia y velocidad |
| Pausa y reanudación | Dos capturas separadas por 300 frames idénticas durante pausa; regreso al juego comprobado |
| Salida mediante END RUN | Regresa a la secuencia de arranque |
| CONTINUE | START durante la cuenta permite volver a la ruta y conducir de nuevo |

Las pruebas de pausa, salida y continuación usaron **botones solamente**, sin escribir WRAM ni congelar temporizadores. Se probaron rutas concretas; el resultado no cubre todas las combinaciones del juego. El BAT de Windows sigue sin ejecución real en Windows: probar una ruta con espacios bajo Linux no sustituye esa comprobación.

## Qué aporta frente a la validación anterior

La revisión anterior comprobaba checksum, descompresión, límites de recursos, reconstrucción y los dos encabezados reparados. Esta ronda añade el comportamiento del distribuble real, las rutas con caracteres especiales, el rechazo de entradas inválidas, la identidad de las tablas de punteros y las transiciones de interfaz que no requieren recorrer rutas completas.

No se detectaron nuevos fallos que bloqueen el juego en estas comprobaciones. No se afirma que todos los estados no visitados estén libres de fallos.

## Situación frente al RC

El reglamento aportado, `WS_TRANSLATION_UNIVERSAL_RULES_v1.1.md`, parte XXI, exige también LANGUAGE, TERMINOLOGY, TYPOGRAPHY, LAYOUT, GRAPHICS y demás controles aplicables en PASS, junto con cero japonés pendiente confirmado, cero BLOCKER y cero MAJOR. Las cuestiones MINOR/POLISH pueden quedar documentadas.

**Mantendría por ahora la etiqueta de build de pruebas.** La barrera principal para RC no es otra partida larga, sino cerrar la evidencia lingüística y visual que falta:

- El inventario ambiental contiene 2.915 gráficos, de los cuales 204 tienen inspección visual de muestra y 2.711 aún no tienen revisión individual. No son 2.711 textos japoneses: falta separar texto, decoración y variantes en perspectiva con evidencia.
- Las cinco fotografías de trenes y algunos posibles rótulos necesitan transcripción/contexto fiable. No se puede convertir su incertidumbre en “cero japonés pendiente”.
- Sigue pendiente la revisión terminológica de AKITA SHINKAN y de abreviaturas del conjunto.
- El ledger actual contiene cinco correcciones recientes, no toda la traducción histórica. Además utiliza `linguistic_approved` y `linguistic_reviewed` en filas diferentes; deben normalizarse sin equiparar revisión con aprobación.
- Bonus/acople, avisos raros y variantes de final requieren comprobaciones dirigidas. RUN ENDED ya tiene validación de su consumidor con acceso asistido; no es necesario repetir una partida larga solo para volver a comprobar sus letras.

Estas son carencias de cobertura o evidencia; no se han contado como errores graves confirmados ni se han degradado automáticamente a problemas menores.

## Siguiente bloque recomendado, sin maratones de juego

1. **Auditoría visual por familias.** Agrupar los gráficos por variantes y revisar hojas de contacto, con registro explícito de qué imágenes se inspeccionan. Identificar únicamente rótulos realmente legibles; no hacer sustituciones automáticas de píxeles ambiguos.
2. **Revisión lingüística del material modificado.** Consolidar las familias históricas traducidas, originales japoneses, traducción y contexto en un ledger uniforme. Revisar nombres, abreviaturas, números, condiciones y límites visuales.
3. **Capturas dirigidas de eventos raros.** Usar los consumidores ya identificados, estados asistidos documentados y límite de tiempo por prueba, comparando con la japonesa cuando sea necesario.
4. **Cerrar la matriz RC.** Separar los PASS comprobados de NEEDS_REVIEW/NEEDS_CONTEXT; autorizar el nombre RC solo cuando cumpla el reglamento. Documentar el pulido menor que se decida conservar.

## Evidencia y reproducción

En el paquete completo, `PRE_RC/` contiene este informe, scripts, resultados JSON y capturas nuevas. El resto conserva íntegramente las fuentes, parches, ROMs y pruebas de v0.4.17.

Desde la raíz del proyecto extraído, usando nombres de salida nuevos:

```sh
python3 tools/qa/run_mesen.py --name mi_options --mode options
python3 tools/qa/run_mesen.py --name mi_pause --frames 6200 --lua PRE_RC/tools/pause_resume.lua
python3 tools/qa/run_mesen.py --name mi_continue --index 5 --frames 14500 --lua PRE_RC/tools/continue_game.lua
```

El auditor del archivo ZIP acepta rutas explícitas:

```sh
python3 PRE_RC/tools/static_prerc.py --archive RUTA_DEL_ZIP_COMPLETO --output CARPETA_NUEVA
```

`SHA256SUMS.txt` corresponde a la entrega base; `PRE_RC/SHA256SUMS_PRE_RC.txt` cubre el checkpoint añadido. El constructor y los parches no cambian. No se publicaron archivos ni se declaró un RC.
