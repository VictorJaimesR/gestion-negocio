# Revisión de seguridad

Fecha: 2026-10-06

Alcance: revisión estática de solo lectura de `gestion-negocio` y
`gestion-negocio-frontend`. No se realizaron pruebas de penetración contra un
servidor desplegado y no se modificó la aplicación.

## Resumen ejecutivo

La aplicación no debería considerarse lista para exposición pública sin corregir
primero el control de acceso a nivel de objeto, la integridad de las
operaciones financieras y la configuración segura de producción. El riesgo
principal es que una cuenta autenticada pueda acceder o modificar información
de otros usuarios y manipular estados financieros.

Si la aplicación es estrictamente monousuario, el hallazgo de control de
acceso tiene menor aplicabilidad; si hay varios usuarios, es directamente
explotable.

## Hallazgos

| # | Severidad | Ubicación | Hallazgo | Confianza |
|---|---|---|---|---|
| 1 | Alta | `config/settings.py:154-161`; `negocios/api_views.py:23-141` | Los `ModelViewSet` requieren autenticación, pero no restringen los registros por propietario, organización, rol o tenant. Un usuario autenticado puede consultar y operar sobre datos de todo el negocio. | 9/10 |
| 2 | Alta | `negocios/serializers.py:179-207`; `negocios/models.py:341-363` | Los movimientos aceptan valores y relaciones financieras controlados por el cliente sin validar de forma suficiente la correspondencia de `tipo`, signo, límites acumulados ni autorización. Además, el guardado actualiza estados financieros derivados. | 9/10 |
| 3 | Alta | `config/settings.py:27-28` | `SECRET_KEY` tiene una clave estática de respaldo. Si falta la variable de entorno en producción, se puede comprometer la firma de sesiones y otros datos firmados por Django. | 9/10 |
| 4 | Alta | `config/settings.py:30-33` | `DEBUG` queda activado por defecto y `ALLOWED_HOSTS` queda vacío si no se configura el entorno. Una excepción puede exponer trazas, rutas y datos internos. | 9/10 |
| 5 | Media | `config/settings.py:150-152`; `gestion-negocio-frontend/src/api.js:1`; `gestion-negocio-frontend/src/components/Login.jsx:12` | El frontend usa una URL HTTP fija y no se observan políticas completas de HTTPS/HSTS, redirección segura ni cookies seguras para producción. Las credenciales o tokens podrían interceptarse fuera de un entorno local. | 8/10 |

## Recomendaciones prioritarias

1. Implementar autorización a nivel de objeto y de organización/tenant,
   filtrando cada consulta por el ámbito autorizado y separando permisos de
   lectura, creación, edición y eliminación.
2. Convertir estados, saldos calculados, fechas de auditoría y campos de
   notificación en campos de solo lectura. Centralizar los cambios financieros
   en servicios de dominio autorizados.
3. Validar explícitamente que el tipo de movimiento coincida con la relación
   asociada, que los valores sean válidos y que los acumulados no excedan el
   importe permitido. Reforzar invariantes con restricciones de base de datos
   cuando sea posible.
4. Eliminar la `SECRET_KEY` de respaldo y fallar el arranque si falta fuera de
   desarrollo. Usar un gestor de secretos y rotar cualquier clave usada fuera
   de entornos locales.
5. Usar `DEBUG=False` por defecto, exigir una lista restrictiva de
   `ALLOWED_HOSTS` y ejecutar `python manage.py check --deploy` en el
   despliegue.
6. Exigir HTTPS en producción, configurar el endpoint del frontend mediante
   variables de entorno, habilitar HSTS y políticas de redirección segura.
   Revisar también expiración y revocación de tokens.
7. Ejecutar una auditoría actualizada de dependencias Python contra una base de
   vulnerabilidades; la revisión estática no sustituye ese análisis.

## Aspectos sin vulnerabilidad explotable confirmada

- No se observaron consultas SQL construidas mediante concatenación; el acceso
  revisado usa el ORM de Django.
- No se observaron sinks evidentes de XSS como `dangerouslySetInnerHTML` o
  `innerHTML` en el frontend.
- La autenticación por token no depende de cookies, por lo que el riesgo CSRF
  clásico no aplica directamente a esos endpoints.
- CORS no usa un comodín y está limitado a un origen local; debe cambiarse a
  HTTPS en producción.
- No se confirmaron endpoints de subida de archivos.

## Limitaciones

Esta revisión fue estática y no incluyó pruebas activas, revisión de la
infraestructura desplegada, configuración real del proxy, pruebas de roles con
usuarios distintos ni una auditoría CVE completa de dependencias. Los secretos
existentes en disco no se incluyen en este documento.
