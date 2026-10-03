# Continuar desde v0.4.17

1. Verificar ROM y hash de PROJECT_STATE.json. RUN ABORTED y RUN ENDED ya tienen glifos reparados; el segundo se validó con transición asistida, no con finalización natural.
2. No tratar la segunda página como bloqueada. Derecha/izquierda cambian de página; confirmar el índice realmente seleccionado después de la animación. Al confirmar curso, el juego intercambia índices 2/3.
3. Priorizar ramas finales por rendimiento, bonus/acople y avisos raros. F000:373A comprueba 0x078F y 0x077F–0x0781; falta relacionarlos con resultados naturales. Mantener límites 85/90 s y cambiar de método si se agota el ensayo.
4. Usar el catálogo de 2.915 recursos ambientales y su inventario. 204 tuvieron inspección visual de muestra; 2.711 no. Todos conservan la original: esto no demuestra que su texto esté traducido. No sustituir rótulos sin transcripción/contexto fiables.
5. Revisar cinco fotografías del banco 02 y la abreviatura AKITA SHINKAN. No contar los gráficos ni sus alias como textos traducibles.
6. Mantener separado: integrado, accesible con botones, asistido, revisado lingüísticamente y revisado visualmente. Consultar exclusions de QA_SUMMARY; dos ensayos iniciales eligieron un curso distinto al solicitado.
7. Cada nueva versión real: constructor reproducible desde original, BPS acumulativo, incremental, fuentes, inventario sin filtros destructivos, checksum, límites de recursos y pruebas del consumidor real.
