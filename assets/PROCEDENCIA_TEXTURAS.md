# Texturas localizadas

Herramienta principal: **ImageGen integrado**, modo `text-localization`, sin API de pago externa. Las texturas de partida proceden del paquete Spanish de PVZF-Translation y conservan su atribución y licencia. Se adapta exclusivamente el texto a español; los PNG se normalizan a las dimensiones que espera el juego.

## Solicitudes de edición

- **Tienda:** cambiar solamente `SHOP` por `TIENDA`, conservando la llave, etiqueta, perspectiva, colores, silueta y transparencia. Salida final: `SelectorScreen_Store.png` y su variante de resaltado.
- **Puzles:** cambiar `PUZZLE` por `PUZLES` en las dos variantes del botón de piedra, conservando inclinación, borde, sombreado, transparencia y proporción original.
- **Odisea:** sustituir los caracteres chinos de la etiqueta de la llave por `ODISEA`, sin modificar la llave, el papel, la inclinación ni la transparencia.
- **Logotipo individual:** `PLANTS → PLANTAS`, `VS → CONTRA`, `ZOMBIES → ZOMBIS`, `FUSION → FUSIÓN`, manteniendo objetos, follaje, proporciones y fondo transparente.
- **Atlas:** se descartó la primera edición conjunta porque movía y unía sprites. Para cada variante se pidió extraer **un solo logotipo aislado**, conservar sus elementos y colores y traducir el título a `PLANTAS CONTRA ZOMBIS FUSIÓN` y el subtítulo a `EDICIÓN COMPLETA`. Se solicitaron por separado las variantes oro, turquesa, azul y estelar.
- **Ajuste estelar:** cambiar únicamente el relleno naranja de `FUSIÓN` a un degradado cian/azul, conservando el resto.

El atlas definitivo mide **2048 × 2048**. Cada resultado aislado se ajusta a los límites visibles de su casilla original, registrados en `texturas.json`. La variante española del tejado que ya existía permanece idéntica. Las variantes descartadas y los archivos intermedios no se distribuyen.

- **Combate y progreso:** sustituir las palabras inglesas por `¡PUM!`, `¡BUM!`, `¡PAM!`, `¡PATAPUM!`, `¡LUZ!`, `¡BOING!`, `¡DESTELLO!`, `¡FUUUM!`, `¡SE ACERCA UNA GRAN OLEADA DE ZOMBIS!` y `PROGRESO DEL NIVEL`. Solicitud común: una sola línea, misma tipografía, color, contorno, inclinación y forma de explosión; fondo realmente transparente y sin texto adicional. Se reutiliza cada sprite traducido en las copias equivalentes Textures/Sprites.
