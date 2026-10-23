# Historial de cambios

## v0.1 — 2026-10-23

### Añadido
- **Proyecto público PvZ Fusion ES**, con localización española ampliada sobre la edición Multi-lang 4.0.5.2 Alpha y licencia CC BY-NC 4.0 con créditos conservados.
- **Catálogo de 720 plantas y 236 zombis**, incluidas variantes y entradas de compatibilidad. Se añaden 38 plantas y 9 zombis que faltaban incluso en el catálogo inglés incluido, contrastando los volcados reales del juego.
- **Cobertura de interfaz y modos:** 3.584 entradas generales, 502 reglas de sustitución, 80 niveles personalizados, 269 cadenas y 90 reglas de esos niveles, 202 consejos de Exhibición de Fusiones y 92 de Yo, Zombi, además de Odisea, Abismo y mecanismos del almanaque.
- **Instaladores de doble clic** para macOS con Sikarugir y Windows, con comprobación SHA-256 de los archivos antes de instalar.
- **Comando `pvz-fusion`**, diagnóstico, consulta de versión y accesos de inicio manuales.
- **Auditoría reproducible** frente al inglés y los volcados reales, más pruebas de conservación de preferencias y partidas.

### Mejorado
- **Terminología compartida** para plantas, zombis y efectos; corrección de consejos que seguían en inglés dentro de los archivos Spanish.
- **Rótulos gráficos en español:** Tienda, Puzles, Odisea, avisos de oleadas, progreso, onomatopeyas de combate y variantes de los logotipos, conservando dimensiones, transparencia y las casillas del atlas.

### Cambiado
- **Actualización automática compatible al abrir:** comprueba la última release española; actualiza el parche y, si hace falta, descarga su base exacta con SHA-256 verificado, conservando los datos del jugador. Espera cuando una base nueva todavía no tiene un parche compatible.
- **Preferencias conservadas:** antes, el gestor reescribía todo MelonPreferences.cfg; ahora solo modifica las claves necesarias del traductor y de la consola.

### Corregido
- **`pvz-fusion: command not found`:** se instala el comando en `.local/bin`, enlazado al único código fuente del proyecto.
- **Pantalla negra en la botella de Sikarugir:** sustitución de las DLL antiguas por el DXMT incluido en el envoltorio y retirada del bloqueo heredado de D3D12. El usuario confirma que vuelve a aparecer el menú.
- **Consola de textos de MelonLoader:** oculta al iniciar y WINEDEBUG desactivado para evitar ventanas y salida de depuración innecesarias.

### Eliminado
- **Actualizador antiguo sin coordinación con el español:** sustituido por actualizaciones vinculadas a una release española y a su base compatible.
- **Dependencia del Whisky retirado** en los puntos de entrada de este proyecto.

### Archivos y pruebas
- Archivos clave: `paquete/Localization/Spanish/`, `pvz_fusion_es.py`, `pvz-fusion`, instaladores, `manifest.json`, `scripts/auditar.py` y `tests/test_installer.py`.
- **11 pruebas pasan** con Python de macOS: conservación de partidas y ajustes, reinstalación, integridad, rutas externas, base incompatible, aplazamiento con el juego abierto y actualización completa simulada del parche junto con una base nueva.
- **Auditoría sin errores:** 9.716 campos, 108 archivos SHA-256, 93 imágenes con dimensiones originales; cobertura del inglés y los volcados reales.
- **Instalación real:** los 108 archivos instalados coinciden con el manifiesto. Comando disponible y diagnóstico correcto. El usuario confirma menú en español y sin consola.
- **Límites:** el instalador Windows necesita una prueba en Windows real; el recuento del catálogo no demuestra haber recorrido todas las partidas y pantallas. La traducción usa asistencia automática con revisión terminológica y técnica.
