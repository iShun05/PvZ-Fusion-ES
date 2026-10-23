# Verificación de seguridad — v0.1

Ámbito: parche local y sus instaladores. No es un servicio web, no ofrece cuentas y no contiene ejecutables del juego. «No aplicable» se refiere a las herramientas de este repositorio, no a la seguridad del juego o de Wine.

| Punto | Estado y evidencia |
|---|---|
| 1. Claves de API | Verificado: no se usan claves ni SDK de pago. El actualizador consulta únicamente releases públicas autorizadas de GitHub. Se revisan los archivos preparados para Git antes de publicar. |
| 2. Secretos en Git | Verificado: revisión del contenido que se añade; partidas, botellas, archivos personales y configuración local excluidos. |
| 3. Claves de base de datos | No aplicable: no hay base de datos ni conexión a ella. |
| 4. RLS | No aplicable: no hay datos de servidor. |
| 5. Cifrado de datos | Verificado en alcance local: las partidas no se suben ni se incluyen en el paquete. Las consultas de actualización usan HTTPS y comunican a GitHub la conexión habitual del cliente. |
| 6. Autenticación | No aplicable: operación local del usuario, sin cuentas propias. |
| 7. Acceso a registros | Verificado en alcance local: el instalador valida la carpeta y copia únicamente la localización; no publica los logs del jugador. |
| 8. Manipulación de campos | Verificado: el manifiesto y las rutas se validan; los errores producen salida fallida. |
| 9. Cookies de sesión | No aplicable: no hay navegador ni sesiones web. |
| 10. Contraseñas | No aplicable: no se solicitan ni guardan. |
| 11. Rate limiting | No aplicable: sin endpoints propios. Se realiza una consulta de GitHub al abrir y descargas solo ante una versión nueva. |
| 12. Bots | No aplicable: sin endpoints ni formularios. |
| 13. Consultas parametrizadas | No aplicable: no hay consultas ni motor de base de datos. |
| 14. Validación de entradas | Verificado: ejecutable, DLL del traductor, manifiesto, sumas y carpeta esperada; prueba de ruta maliciosa. |
| 15. Contenido no confiable | Verificado en alcance local: JSON se analiza como datos; no se usa eval ni se ejecuta contenido de la traducción. |
| 16. Restricción de archivos | Verificado: solo se instalan archivos del manifiesto dentro de la localización, tras validar hashes y rutas. |
| 17. Datos mínimos | Verificado: el diagnóstico muestra versión y disponibilidad, sin leer ni enviar el contenido de partidas. |
| 18. Cabeceras | No aplicable: no se despliega web ni API. |
| 19. HTTPS | Verificado: consultas y descargas por HTTPS; lista de repositorios autorizados, SHA-256 del asset y de los binarios base. Sin desactivar validación TLS. |
| 20. Dependencias | Verificado para el código propio: Python usa biblioteca estándar y PowerShell componentes del sistema. No se empaquetan bibliotecas nativas ni dependencias transitivas. El juego, .NET y MelonLoader se obtienen por separado del proyecto original. |

La integridad SHA-256 detecta archivos dañados respecto al manifiesto recibido; no sustituye la confianza en el origen de la descarga ni una firma criptográfica del editor. El proceso de pruebas no garantiza ausencia de vulnerabilidades. La instalación de Windows queda pendiente de verificación en un sistema Windows real.

La lista de lanzamiento de una web de producción no aplica: este proyecto distribuye un parche mediante GitHub y no publica una web, formularios, cookies ni analítica.
