<p align="center"><a href="README.md" lang="en">English</a> · <strong>Español</strong></p>

<h1 align="center">Brand Machines</h1>

<p align="center"><strong>El método para agentes.</strong></p>

<p align="center">
  Diagnostica, diseña y revisa sistemas de marca.<br>
  Siete capas, principios de decisión y fuentes verificables.<br>
  <sub>Un método de Viktor Berthelius.</sub>
</p>

<p align="center">
  <a href="https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.0"><img src="https://img.shields.io/badge/v0.2.0-e63946?style=flat-square" alt="Versión 0.2.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licencia-MIT-1a1a1a?style=flat-square" alt="Licencia MIT"></a>
  <a href="#el-guardián-en-acción"><img src="https://img.shields.io/badge/Python-3.10%2B-1a1a1a?style=flat-square" alt="Comprobador local: Python 3.10 o posterior"></a>
</p>

<p align="center">
  <a href="#instalar"><strong>Instalar</strong></a> ·
  <a href="#tres-formas-de-trabajar">Usar</a> ·
  <a href="#documentación">Documentación</a> ·
  <a href="https://machines.brthls.com">El libro y el sistema</a>
</p>

---

<p align="center">
  <strong>Núcleo · Mente · Cuerpo · Piel</strong><br>
  <strong>Motores · Brand OS · Interconexiones</strong>
</p>

> El método es compartido. La identidad de cada marca es propia.

Esta skill adapta *Brand Machines: Teoría general de los sistemas de marca* al trabajo de un agente. El paquete de referencia incluido describe Brand Machines; sus fuentes, estilo y decisiones no se imponen a otras marcas.

## Instalar

Desde el proyecto donde quieras usar la skill:

```sh
npx skills add berthelius/brand-machines-agents --skill brand-machines
```

**Disponible en español e inglés.** Instalación verificada en **Codex** y **Claude Code**. El instalador permite elegir los agentes y el alcance.

| Agente | Invocación |
| :--- | :--- |
| Codex | `$brand-machines` |
| Claude Code | `/brand-machines` |

<details>
<summary>Instalación manual y otros agentes</summary>

Descarga el repositorio o la [release](https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.0) y copia la carpeta completa `skills/brand-machines` —o `brand-machines` dentro del ZIP— al directorio de skills de tu agente. Conserva `references`, `scripts`, `assets` y `agents` junto a `SKILL.md`.

La documentación funciona con cualquier agente capaz de leer esos archivos; la detección automática depende del entorno. Python 3.10 o posterior es necesario solo para ejecutar el comprobador local, que no tiene dependencias externas.

</details>

El agente responde en tu idioma. Para el comprobador local, usa `--language es` o `--language en`: selecciona la identidad y las reglas de ese idioma. Los comandos antiguos sin flag siguen usando el paquete español. Con `--pack`, manda el idioma del paquete.

## Tres formas de trabajar

### 01 · Diagnosticar

> Usa Brand Machines para diagnosticar esta marca con los documentos adjuntos. Distingue evidencia, inferencias e información pendiente por capa.

### 02 · Proponer

> Aplica Brand Machines a este brief. Deriva la propuesta de nuestros principios, explica el trade-off y señala las decisiones aún no aprobadas.

### 03 · Revisar

> Actúa como Guardián de esta propuesta. Contrasta las afirmaciones con sus fuentes y la decisión con el Núcleo. Permite variaciones coherentes y sugiere una corrección cuando proceda.

## El Guardián, en acción

Una demostración del capítulo 17, después de clonar el repositorio y desde su raíz:

```sh
python3 skills/brand-machines/scripts/bm.py review \
  --input skills/brand-machines/assets/examples/chapter-17.json
```

**Pieza:** «La MEJOR oferta del año!!!!»

**Resultado:** `revise`, con `no_superlativos` y `exclamaciones_excesivas`, sus fuentes y sugerencias de revisión. El código de salida 1 es el esperado en este ejemplo.

**El comprobador aplica reglas explícitas. El agente realiza la revisión semántica.** Una pieza sin incidencias mecánicas devuelve `needs_review`: todavía requiere juicio sobre su coherencia.

<details>
<summary>Validar el paquete, diagnosticar y probar una variación</summary>

```sh
python3 skills/brand-machines/scripts/bm.py validate
python3 skills/brand-machines/scripts/bm.py diagnose
python3 skills/brand-machines/scripts/bm.py review \
  --input skills/brand-machines/assets/examples/variation.json
```

La variación devuelve `needs_review`. El ejemplo `semantic-contradiction.json` muestra por qué: una decisión puede superar las comprobaciones léxicas y contradecir la definición de Brand Machine.

Los comandos `review`, `diagnose`, `validate` y `serve` aceptan `--pack ruta/brand.json` para usar otra identidad.

</details>

<details>
<summary>API local · sin claves ni llamadas a modelos</summary>

```sh
python3 skills/brand-machines/scripts/bm.py serve
```

En otra terminal:

```sh
curl http://127.0.0.1:8765/api/v1/validate \
  -H 'Content-Type: application/json' \
  --data '{"type":"copy","content":"La MEJOR oferta del año!!!!","context":"email_subject"}'
```

La API expone el mismo comprobador y escucha solo en tu máquina. No necesita claves, no realiza llamadas a modelos y no publica piezas. No es un servicio público alojado.

</details>

<details>
<summary>Qué acredita cada comprobación</summary>

| Parte | Acredita | No acredita |
| :--- | :--- | :--- |
| `validate` | Estructura del paquete e integridad de fuentes | Veracidad de las fuentes |
| `diagnose` | Cobertura documental por capa | Madurez de la marca |
| `review` / API | Comprobaciones declaradas y presencia/vigencia de referencias | Coherencia semántica total ni verdad de afirmaciones |
| Skill aplicada por un agente | Una revisión razonada dentro del alcance y fuentes disponibles | Autorización automática para publicar |

</details>

## Documentación

| Referencia | Contenido |
| :--- | :--- |
| [Método](skills/brand-machines/references/method.md) | Las siete capas y sus relaciones. |
| [Procedimientos](skills/brand-machines/references/workflows.md) | Diagnóstico, propuesta y revisión. |
| [Contrato del Guardián](skills/brand-machines/references/review.md) | Criterios, hallazgos y alcance de la revisión. |
| [Formato del paquete](skills/brand-machines/references/pack.md) | Cómo representar otra identidad y sus fuentes. |
| [Procedencia editorial](skills/brand-machines/references/provenance.json) | Fuentes de esta adaptación. |

<details>
<summary>Desarrollo y pruebas</summary>

```sh
python3 -m unittest discover -s tests -v
```

Las pruebas automatizadas cubren el código local. Los escenarios del [contrato del Guardián](skills/brand-machines/references/review.md) sirven para evaluar por separado el comportamiento del agente. Una suite mecánica verde no acredita una evaluación semántica. [Ver CI](https://github.com/berthelius/brand-machines-agents/actions/workflows/verify.yml).

</details>

La v0.2.0 contiene una skill bilingüe autosuficiente, una identidad de referencia y cuatro piezas de demostración en cada idioma, y un comprobador compartido. OpenDesign, exportaciones SOUL.md y un servidor MCP quedan para integraciones posteriores.

---

<p align="center">
  <strong>Brand Machines</strong><br>
  <sub>Teoría general de los sistemas de marca · Viktor Berthelius</sub><br><br>
  <a href="https://www.brthls.com/book">El libro</a> ·
  <a href="https://machines.brthls.com">machines.brthls.com</a> ·
  <a href="https://www.brthls.com">brthls.com</a>
</p>

<p align="center"><sub>MIT para los archivos de esta distribución. El manuscrito completo y su repositorio editorial privado quedan fuera de ella. No se conceden derechos sobre marcas de terceros.</sub></p>
