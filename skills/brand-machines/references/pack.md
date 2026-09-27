# Paquete de identidad 0.1

El archivo `brand.json` es un formato local de esta implementación. No declara conformidad con BCP, MRBS u otro estándar externo. El ejemplo funcional está en `../assets/brand-machines/brand.json` respecto de la raíz de referencias.

| Campo | Contenido |
|---|---|
| `schema_version` | `"0.1"` |
| `language` | `"es"` o `"en"`; opcional, por compatibilidad los paquetes antiguos son ES |
| `id`, `name`, `version` | Identificador, nombre y versión de la marca |
| `sources` | Fuentes locales con `id`, `title`, `path`, `sha256`; `valid_until` opcional (AAAA-MM-DD) |
| `layers` | Siete objetos ordenados: `id` 1–7, `name` canónico, `summary`, `sources` |
| `principles` | `id`, `layer`, `name`, `definition`, `situations`, `tradeoff`, `example`, `counterexample`, `sources` |
| `checks` | Comprobaciones que concretan un principio en un contexto |

Los seis campos de un valor operable son los del capítulo 11. Los IDs, referencias y metadatos de versión son convenciones de implementación. Las capas y los principios pueden quedar sin fuentes durante el diagnóstico; el Guardián devolverá `needs_evidence`. Una capa desconocida conserva su nombre y un `summary` vacío.

Las rutas de fuentes se resuelven desde la carpeta de `brand.json` y deben permanecer dentro de ella. El comprobador verifica su hash y su caducidad declarada; no accede a la red. Revisa el contenido de una fuente antes de actualizar el hash con `hashlib.sha256(path.read_bytes()).hexdigest()`. La integridad no acredita que la fuente sea cierta ni que respalde una afirmación concreta.

## Idioma

`--language es` o `--language en` selecciona la identidad de referencia y sus comprobaciones; no traduce contenido ni detecta idiomas. Sin el flag se mantiene el paquete español. Con `--pack`, el idioma declarado por ese paquete gobierna el resultado; un flag explícito contradictorio se rechaza. Los nombres canónicos ingleses son Core, Mind, Body, Skin, Engines, Brand OS e Interconnections, en ese orden. No mezclar nombres de ambos idiomas en un paquete.

Los IDs de reglas, las claves JSON, los estados y los códigos de salida se conservan entre idiomas. Los mensajes, fuentes y nombres de capas se localizan. La pieza admite `language` opcional: si se declara, debe coincidir con el paquete. Sin ese campo, el llamante elige el idioma correcto; el comprobador no lo adivina. Para contenido mixto, revisar cada idioma con su paquete.

`serve --language en` inicia la misma API local con el paquete inglés para todas las peticiones; no hay negociación HTTP de idiomas. Reiniciar el servidor para cambiar de idioma. Los errores de validación se localizan; errores nativos del sistema operativo y mensajes estándar de argparse mantienen el idioma del entorno.

## Comprobaciones admitidas

Todas contienen `id`, `kind`, `principle`, `contexts`, `message` y `suggestion`. `contexts` enumera los contextos exactos donde se aplica; `"*"` aplica a todos. La comprobación hereda capa y fuentes del principio.

- `forbidden_terms`: añade `terms`, una lista de coincidencias literales con límites de palabra, sin distinguir mayúsculas. No interpreta negaciones, citas ni superlativos nuevos.
- `max_exclamations`: añade `maximum`, entero de 0 a 100. Cuenta `¡` y `!`.
- `canonical_layers`: compara el campo estructurado opcional `layers` de la pieza con las siete capas. No extrae taxonomías de prosa libre.

Las comprobaciones léxicas son señales para revisar en contexto. No constituyen una gramática universal ni deben reemplazar el juicio del Guardián.

## Pieza de entrada

```json
{
  "type": "copy",
  "context": "email_subject",
  "content": "La MEJOR oferta del año!!!!"
}
```

Opcionalmente, `claims` contiene objetos `{ "text": "fragmento literal", "sources": ["id-fuente"] }`. La afirmación debe aparecer en el contenido. Fuentes ausentes, desconocidas o caducadas producen `needs_evidence`. Un `claims` vacío no demuestra que no haya afirmaciones: el agente debe leer el contenido completo. El campo opcional `layers` contiene los nombres de la arquitectura que presenta una pieza.

## Salida y códigos

`review` devuelve `revise` si detecta incidencias, `needs_evidence` si falta sustento documental y `needs_review` cuando las comprobaciones ejecutadas no detectan problemas. Siempre conserva `semantic_review: "pending"` y `publication_authorized: false`. Si hay incidencias y faltan fuentes a la vez, devuelve `revise` y conserva ambas listas.

Código 0: comando correcto sin incidencias mecánicas detectadas. Código 1: revisión con incidencias o evidencia pendiente. Código 2: entrada, paquete o lectura inválidos. El código 0 de `diagnose` solo significa que se generó el diagnóstico; consulta `missing_layers`.

La API devuelve HTTP 200 para un dictamen generado, 400 para datos inválidos, 413 para exceso de tamaño y 415 para un tipo de contenido distinto de JSON. Es un servicio local de demostración, ligado a un paquete conocido. No es un servidor público de producción ni un servicio de inferencia.
