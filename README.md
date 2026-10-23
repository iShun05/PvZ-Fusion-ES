# PvZ Fusion ES

Parche comunitario en español para **PvZ Fusion 4.0.5.2 Multi-lang Alpha**: amplía los diccionarios, el almanaque, los consejos y los rótulos gráficos. Incluye instalación manual para macOS con Sikarugir y Windows. **No incluye el juego, la botella, MelonLoader ni partidas guardadas.**

## Descargar e instalar

[**Descargar PvZ-Fusion-ES.zip**](https://github.com/iShun05/PvZ-Fusion-ES/releases/latest/download/PvZ-Fusion-ES.zip) · [Última versión y notas](https://github.com/iShun05/PvZ-Fusion-ES/releases/latest)

1. Ten instalada la [versión Multi-lang 4.0.5.2 del proyecto original](https://github.com/Teyliu/PVZF-Translation/releases/tag/4.0.5_alpha). El parche necesita su `PvZ_Fusion_Translator.dll`, MelonLoader y los requisitos de .NET del juego. No lo apliques sobre la edición china sin mods ni sobre otras versiones.
2. Cierra el juego desde su propio menú y descomprime `PvZ-Fusion-ES.zip`.
3. **Mac:** conserva la carpeta del parche en una ubicación estable y abre `Instalar_macOS.command`. La botella debe estar en `/Applications/Sikarugir/PvZ Fusion.app`. Después abre la app o escribe `pvz-fusion` en una terminal nueva. También puedes abrir `Jugar_macOS.command`.
4. **Windows:** abre `Instalar_Windows.bat`, selecciona la carpeta **Game Files** de la instalación Multi-lang y, al finalizar, abre el archivo **Jugar_Windows.bat que se ha copiado a Game Files**.

El instalador verifica el paquete, selecciona español local y oculta la consola. Conserva las partidas y los ajustes de otros mods. En Windows puede descargar la base compatible si la instalación es de otra versión.

**Requisitos:** macOS con Sikarugir y Python 3 de las herramientas de Apple, o Windows con Windows PowerShell y el juego Multi-lang funcional. El instalador de Mac usa `/usr/bin/python3`; si no está disponible, instala las herramientas de línea de comandos de Apple antes de continuar. En Windows no hace falta Python. La instalación de Windows requiere comprobarse en un equipo Windows real; las pruebas de instalación de esta versión se realizan en macOS.

**Avisos del sistema:** al abrir un `.command`, macOS puede pedir autorización o la instalación de las herramientas de Apple. Comprueba el origen del archivo antes de abrirlo. Windows puede mostrar un aviso de archivo descargado; verifica que proceda de este repositorio. No desactives Gatekeeper, SmartScreen ni el antivirus.

## Versión y alcance

**Versión actual: v0.1** · base compatible: **4.0.5.2 Multi-lang Alpha**.

El catálogo del parche contiene 720 entradas de plantas y 236 de zombis, incluidas variantes y entradas de compatibilidad que pueden no aparecer en todas las partidas. Se contrastan tanto el inglés incluido como los volcados reales del juego: comparar únicamente con inglés dejaba fuera 38 plantas y 9 zombis de la instalación examinada.

El objetivo es cubrir el español del contenido accesible. La cobertura del catálogo se puede medir; recorrer todas las combinaciones, desafíos y textos que solo aparecen durante una partida requiere pruebas de juego adicionales. No se presenta una auditoría de archivos como garantía de haber visto todas las pantallas.

## Funciones principales

- Diccionarios de interfaz y expresiones con sus variables de sustitución.
- Nombres, descripciones, estadísticas y costes del almanaque.
- Consejos de Yo, Zombi, Exhibición de Fusiones, niveles personalizados, Odisea y Abismo.
- Rótulos del menú y variantes visuales en español.
- `pvz-fusion` y actualizaciones automáticas al abrir, tanto del parche español como de la base declarada compatible.
- Corrección de la botella de PvZ Fusion: DXMT del propio Sikarugir, retirada del bloqueo heredado de D3D12 y consola oculta. No descarga motores ni modifica otras botellas.

La versión del parche y el contacto aparecen en la información traducida, en `pvz-fusion --version`, en `pvz-fusion diagnostico` y en `UserData/PvZ-Fusion-ES.json`.

## Tecnología y estructura

Python 3 y biblioteca estándar para macOS; PowerShell para Windows; JSON y PNG para la localización. No requiere claves de API, cuentas nuevas, servicios de pago ni tareas programadas. Consulta las releases públicas de GitHub al abrir el juego.

```text
paquete/Localization/Spanish/    Localización que se instala
pvz_fusion_es.py                Instalador y lanzador de Mac
pvz-fusion                     Comando de terminal
Instalar_macOS.command         Instalación con doble clic en Mac
Instalar_Windows.bat / .ps1     Instalación con doble clic en Windows
Jugar_*.command / .bat          Accesos de inicio
manifest.json                  Inventario SHA-256 de la distribución
actualizaciones.py / .json     Actualización y base compatible
Actualizar_Windows.ps1         Actualizador del lanzador Windows
scripts/                       Auditoría y generación del manifiesto
pruebas/                       Resultado de las verificaciones
```

La traducción se ha completado con asistencia automática y revisión de terminología y estructura. Los nombres se normalizan mediante un glosario y las etiquetas, cifras y variables se conservan fuera de la traducción de los fragmentos. La revisión lingüística continua permite corregir giros poco naturales sin alterar las mecánicas.

## Compilar, instalar y verificar

No hay que compilar el parche. Para una instalación de Mac por terminal:

```bash
./pvz-fusion instalar
./pvz-fusion diagnostico
./pvz-fusion jugar
```

Para comprobar un catálogo frente a tu instalación:

```bash
python3 scripts/auditar.py --game-dir "/ruta/a/Game Files"
```

El auditor revisa JSON, identificadores duplicados, entradas ausentes, textos chinos visibles y marcadores residuales. Los nombres chinos de las claves son identificadores que el mod necesita para encontrar el texto original: no son textos visibles que hayan quedado sin traducir.

## Actualizaciones automáticas

**Se comprueban al abrir el juego**, sin intervención manual: desde la app de Sikarugir, `pvz-fusion` o el lanzador `Jugar_Windows.bat`. También puedes ejecutar `pvz-fusion actualizar` con el juego cerrado.

El actualizador consulta la última release de este repositorio. Si trae un parche nuevo, comprueba el SHA-256 del ZIP y lo instala. Si ese parche necesita otra base, descarga la versión original exacta indicada en `actualizacion.json`, comprueba sus hashes y conserva `UserData`, las partidas externas a Game Files y los archivos adicionales del jugador. Las descargas temporales se eliminan al terminar. En un checkout Git limpio, el código avanza al tag mediante fast-forward; los cambios locales se respetan y aplazan la actualización.

**Una versión del juego sin parche español compatible todavía no se instala.** Así se evita perder el idioma o introducir una base sin comprobar. El actualizador no traduce contenido nuevo por sí mismo: la compatibilidad y los nuevos textos deben publicarse en una release española. Sin conexión o con el juego abierto, se conserva la instalación actual. No hay un proceso residente ni comprobaciones mientras el juego está cerrado.

En Windows abre siempre `Jugar_Windows.bat`; ejecutar directamente el `.exe` omite la comprobación. En macOS el instalador integra la comprobación en `StartupScript` del envoltorio. Los registros de actualización se guardan en la carpeta temporal del usuario.

## Versiones y código fuente

| Versión | Fecha | Cambios | Código |
|---|---|---|---|
| [`v0.1`](https://github.com/iShun05/PvZ-Fusion-ES/releases/tag/v0.1) **(actual)** | 2026-10-23 | Primera edición del catálogo ampliado, instaladores y reparación del arranque en Sikarugir. | [Ver código](https://github.com/iShun05/PvZ-Fusion-ES/tree/v0.1) · [ZIP](https://github.com/iShun05/PvZ-Fusion-ES/archive/refs/tags/v0.1.zip) |

```bash
git checkout v0.1
```

## Créditos y licencia

Obra derivada de [Teyliu/PVZF-Translation](https://github.com/Teyliu/PVZF-Translation), con su traducción comunitaria española como base. Se conserva la licencia **CC BY-NC 4.0** y la atribución. El juego y sus personajes pertenecen a sus respectivos titulares; este parche no implica respaldo oficial. Consulta [CREDITOS.md](CREDITOS.md) y [LICENSE](LICENSE).

## Contacto

[Instagram de iShun05](https://www.instagram.com/_shun._05/) · [Informar de un texto pendiente o un fallo](https://github.com/iShun05/PvZ-Fusion-ES/issues).
