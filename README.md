# Brand Machines para agentes

El método de **Viktor Berthelius** para diagnosticar, diseñar y revisar sistemas de marca, en una skill instalable. Siete capas, principios de decisión y fuentes verificables.

[El libro](https://www.brthls.com/book) · [Brand Machines](https://machines.brthls.com) · [Método](skills/brand-machines/references/method.md) · [Contrato del Guardián](skills/brand-machines/references/review.md) · [Formato del paquete](skills/brand-machines/references/pack.md)

**v0.1.0 · Español · MIT · Python sin dependencias para las comprobaciones locales.**

## Instalar

Desde el proyecto donde quieras usar la skill:

```sh
npx skills add berthelius/brand-machines-agents --skill brand-machines
```

El instalador permite elegir los agentes y el alcance. Alternativamente, descarga el repositorio y copia la carpeta completa `skills/brand-machines` al directorio de skills de tu agente. Conserva `references`, `scripts`, `assets` y `agents` junto a `SKILL.md`. La documentación funciona con cualquier agente capaz de leer esos archivos; la detección automática depende del entorno.

En Codex puedes invocarla como `$brand-machines`; en Claude Code, como `/brand-machines` después de instalarla en su directorio de skills. Python 3.10 o posterior es necesario solo para ejecutar el comprobador local.

## Usar

**Diagnosticar:** «Usa Brand Machines para diagnosticar esta marca con los documentos adjuntos. Distingue evidencia, inferencias e información pendiente por capa».

**Proponer:** «Aplica Brand Machines a este brief. Deriva la propuesta de nuestros principios, explica el trade-off y señala las decisiones aún no aprobadas».

**Revisar:** «Actúa como Guardián de esta propuesta. Contrasta las afirmaciones con sus fuentes y la decisión con el Núcleo. Permite variaciones coherentes y sugiere una corrección cuando proceda».

El método es compartido. La identidad de cada marca es propia. El paquete de referencia incluido describe Brand Machines: sus fuentes, estilo y decisiones no se imponen a otras marcas.

## Una demostración del capítulo 17

Después de clonar el repositorio, desde su raíz:

```sh
python3 skills/brand-machines/scripts/bm.py validate
python3 skills/brand-machines/scripts/bm.py diagnose
python3 skills/brand-machines/scripts/bm.py review \
  --input skills/brand-machines/assets/examples/chapter-17.json
```

La tercera orden revisa «La MEJOR oferta del año!!!!». Devuelve `revise` con `no_superlativos` y `exclamaciones_excesivas`, las fuentes que sustentan esas comprobaciones y sugerencias de revisión. Sale con código 1 porque encontró incidencias; es el resultado esperado.

Para una variación expresiva sin incidencias mecánicas:

```sh
python3 skills/brand-machines/scripts/bm.py review \
  --input skills/brand-machines/assets/examples/variation.json
```

Devuelve `needs_review`, no una aprobación. La revisión semántica corresponde al agente que lee la skill y contrasta la pieza con las fuentes. El ejemplo `semantic-contradiction.json` hace visible esa frontera: una decisión puede superar las comprobaciones léxicas y contradecir la definición de Brand Machine.

## API local

```sh
python3 skills/brand-machines/scripts/bm.py serve
```

En otra terminal:

```sh
curl http://127.0.0.1:8765/api/v1/validate \
  -H 'Content-Type: application/json' \
  --data '{"type":"copy","content":"La MEJOR oferta del año!!!!","context":"email_subject"}'
```

La API expone el mismo comprobador y escucha solo en tu máquina. No necesita claves, no realiza llamadas a modelos y no publica piezas. No es un servicio público alojado. Los comandos `review`, `diagnose`, `validate` y `serve` aceptan `--pack ruta/brand.json` para usar otra identidad.

## Qué acredita cada parte

| Parte | Acredita | No acredita |
|---|---|---|
| `validate` | Estructura del paquete e integridad de fuentes | Veracidad de las fuentes |
| `diagnose` | Cobertura documental por capa | Madurez de la marca |
| `review` / API | Comprobaciones declaradas y presencia/vigencia de referencias | Coherencia semántica total ni verdad de afirmaciones |
| Skill aplicada por un agente | Una revisión razonada dentro del alcance y fuentes disponibles | Autorización automática para publicar |

La primera versión contiene una skill autosuficiente, una identidad de referencia, cuatro piezas de demostración y pruebas del comprobador. OpenDesign, exportaciones SOUL.md y un servidor MCP quedan para integraciones posteriores; no se anuncian como implementados.

## Desarrollar

```sh
python3 -m unittest discover -s tests -v
```

Las pruebas automatizadas cubren el código local. Los escenarios del [contrato del Guardián](skills/brand-machines/references/review.md) sirven para evaluar por separado el comportamiento del agente. No se confunde una suite mecánica verde con una evaluación semántica.

[Procedencia editorial](skills/brand-machines/references/provenance.json): adaptación operativa de *Brand Machines: Teoría general de los sistemas de marca*. El libro completo y su repositorio editorial privado no forman parte de esta distribución. La licencia MIT cubre los archivos de este repositorio; no concede derechos sobre el manuscrito completo ni sobre marcas de terceros.

Viktor Berthelius · [brthls.com](https://www.brthls.com)
