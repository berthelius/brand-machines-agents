<p align="right"><a href="README.md" lang="en">English</a> · <strong>Español</strong></p>

<p align="center">
  <img src="assets/readme/fig-hero-agent-edition.svg" width="100%" alt="Brand Machines, de Viktor Berthelius. Siete capas conectadas descansan sobre el Núcleo, representado en rojo.">
</p>

<h1 align="center">Una marca vive en sus decisiones.</h1>

<p align="center">
  El método del libro, al alcance de tus agentes.<br>
  <sub>Diagnosticar la identidad. Generar propuestas. Revisar la coherencia.</sub>
</p>

<p align="center">
  <a href="#instalar"><strong>Instalar la skill</strong></a> &nbsp;·&nbsp;
  <a href="#el-método">El método</a> &nbsp;·&nbsp;
  <a href="#patagonia">Patagonia</a> &nbsp;·&nbsp;
  <a href="#el-libro">El libro</a>
</p>

<p align="center">
  <a href="https://skills.sh/berthelius/brand-machines-agents/brand-machines"><img src="https://img.shields.io/badge/Agent_Skill-ES_%2F_EN-1A1A1A?style=flat-square&amp;labelColor=1A1A1A" alt="Agent Skill en español e inglés"></a>
  <a href="https://github.com/berthelius/brand-machines-agents/actions/workflows/verify.yml"><img src="https://github.com/berthelius/brand-machines-agents/actions/workflows/verify.yml/badge.svg" alt="Estado de CI del comprobador local"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-1A1A1A?style=flat-square&amp;labelColor=1A1A1A" alt="Licencia MIT"></a>
</p>

<br>

Una marca revela su identidad en lo que elige, en lo que rechaza y en lo que está dispuesta a sacrificar. Sus principios deben seguir siendo útiles cuando cambia el encargo.

**Brand Machines** lleva el método de Viktor Berthelius al trabajo de un agente. Dale los documentos de una marca y una tarea: puede examinar su identidad, formular propuestas y revisar decisiones con sus principios y fuentes. El método es compartido. **La identidad de cada marca es propia.**

## Instalar

Desde el proyecto donde quieras usar la skill:

```sh
npx skills add berthelius/brand-machines-agents --skill brand-machines
```

<p><strong>Codex</strong> &nbsp;<code>$brand-machines</code> &nbsp;·&nbsp; <strong>Claude Code</strong> &nbsp;<code>/brand-machines</code></p>

Instalación verificada en ambos. Elige el agente y el alcance en el instalador y dale un encargo:

> Aplica Brand Machines a este brief y a los documentos de nuestra marca. Propón tres direcciones distintas, explica el principio y el trade-off de cada una y revisa su coherencia. Separa evidencia, inferencias y decisiones que todavía necesitan aprobación.

<details>
<summary>Instalación manual y otros agentes</summary>

Descarga el repositorio o la [release](https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.1) y copia la carpeta completa `skills/brand-machines` —o `brand-machines` dentro del ZIP— al directorio de skills de tu agente. Conserva `references`, `scripts`, `assets` y `agents` junto a `SKILL.md`.

La documentación funciona con cualquier agente capaz de leer esos archivos; la detección automática depende del entorno. Python 3.10 o posterior es necesario solo para ejecutar el comprobador local, que no tiene dependencias externas.

El agente responde en tu idioma. Para el comprobador local, usa `--language es` o `--language en`: selecciona la identidad y las reglas de ese idioma. Los comandos antiguos sin flag siguen usando el paquete español. Con `--pack`, manda el idioma del paquete.

</details>

<br>

## El método

Siete capas conectadas, desde los principios que definen una identidad hasta su contacto con el mundo.

| Capa | Qué examina el agente |
| :--- | :--- |
| **Núcleo** | Propósito, valores operables y visión. |
| **Mente** | Inteligencia distribuida y principios de decisión. |
| **Cuerpo** | La arquitectura modular que estructura la expresión. |
| **Piel** | La expresión visual, verbal, sonora y táctil. |
| **Motores** | Sistemas generativos que producen output de marca. |
| **Brand OS** | Workflows e integraciones que orquestan las capas. |
| **Interconexiones** | Puntos de contacto con ecosistemas externos. |

Una decisión en una capa tiene consecuencias en las demás. El agente sigue esas relaciones, distingue variación expresiva de contradicción y registra lo que la evidencia disponible no permite establecer.

**Diagnosticar** para entender el sistema. **Proponer** para convertir principios en alternativas. **Revisar** para examinar una pieza y sugerir una corrección. [Leer el método →](skills/brand-machines/references/method.md)

<br>

## Patagonia

### Una chaqueta. Dos decisiones coherentes.

Reparar una chaqueta que todavía puede cumplir su función. Considerar una sustitución cuando no se puede recuperar un uso necesario. El mismo principio puede sostener ambas decisiones; el contexto importa.

El caso sitúa esa distinción junto a otros tres mensajes, entre ellos una afirmación ambiental absoluta y una promesa de reparación que su cita no respalda.

<p>
  <strong>4 fuentes primarias &nbsp;·&nbsp; 5 situaciones hipotéticas</strong><br>
  <sub>Un paquete de fuentes, comprobaciones locales registradas, revisión semántica comentada y correcciones propuestas.</sub>
</p>

**[Leer el caso Patagonia →](skills/brand-machines/assets/case-studies/patagonia/README.es.md)**

Estudio educativo independiente, sin respaldo de Patagonia. El mismo asistente preparó los casos y los comentarios; no constituye una evaluación independiente del modelo. Cuatro capas sin documentación se mantienen explícitamente desconocidas.

<details>
<summary>Reproducir las comprobaciones locales</summary>

Después de clonar este repositorio, desde su raíz:

```sh
python3 skills/brand-machines/assets/case-studies/patagonia/run.py
```

Python 3.10 o posterior, sin dependencias externas ni llamadas a modelos. El script reproduce comprobaciones mecánicas de los mensajes en inglés; la [revisión comentada](skills/brand-machines/assets/case-studies/patagonia/semantic-review.md) contiene los juicios semánticos por separado. El código de salida 0 confirma las comprobaciones del ejercicio, no la aprobación de los mensajes.

</details>

<br>

## El Guardián local

La skill aporta al agente un método para juzgar. El comprobador opcional en Python verifica estructura, integridad de fuentes y reglas explícitas. **Superar esas comprobaciones deja pendiente la revisión semántica.** Las identidades de referencia incluidas describen Brand Machines; su estilo y sus fuentes no se imponen a otras marcas.

<details>
<summary>Probar el ejemplo del capítulo 17</summary>

Después de clonar el repositorio, desde su raíz:

```sh
python3 skills/brand-machines/scripts/bm.py review \
  --input skills/brand-machines/assets/examples/chapter-17.json
```

**Pieza:** «La MEJOR oferta del año!!!!»

**Resultado:** `revise`, con `no_superlativos` y `exclamaciones_excesivas`, sus fuentes y sugerencias de revisión. Se espera el código de salida 1.

</details>

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

<br>

## El libro

<p align="center">
  <a href="https://machines.brthls.com/#book"><img src="assets/readme/cover-es.webp" width="200" alt="Cubierta de Brand Machines: Teoría general de los sistemas de marca, de Viktor Berthelius."></a>
</p>

<p align="center">
  <strong>Brand Machines</strong><br>
  <em>Teoría general de los sistemas de marca</em><br>
  Viktor Berthelius
</p>

El libro desarrolla el argumento: la identidad como sistema generativo, la coherencia mediante principios y la arquitectura que las hace posibles. Este repositorio adapta parte de ese método para agentes. Puedes usar la skill sin comprar el libro.

<p align="center">
  <a href="https://machines.brthls.com/#book"><strong>Explorar el libro →</strong></a> &nbsp;·&nbsp;
  <a href="https://machines.brthls.com/">El proyecto</a> &nbsp;·&nbsp;
  <a href="https://github.com/berthelius">El autor</a>
</p>

<br>

## Referencias y desarrollo

| Referencia | Punto de partida para… |
| :--- | :--- |
| [Método](skills/brand-machines/references/method.md) | Las siete capas y sus relaciones. |
| [Procedimientos](skills/brand-machines/references/workflows.md) | Diagnóstico, propuesta y revisión. |
| [Contrato del Guardián](skills/brand-machines/references/review.md) | Hallazgos, fuentes y alcance del juicio. |
| [Formato del paquete](skills/brand-machines/references/pack.md) | La identidad y evidencia de tu propia marca. |
| [Procedencia editorial](skills/brand-machines/references/provenance.json) | Fuentes y terminología de la adaptación. |
| [Contribuir](CONTRIBUTING.md) | Casos documentados, correcciones y mejoras de idioma. |

<details>
<summary>Pruebas y estado de la release</summary>

```sh
python3 -m unittest discover -s tests -v
python3 skills/brand-machines/assets/case-studies/patagonia/run.py
```

CI se ejecuta en Python 3.10, 3.12 y 3.14. Las pruebas cubren código local, separación de idiomas y ejemplos mecánicos; no acreditan precisión del modelo ni corrección semántica. [Ver CI](https://github.com/berthelius/brand-machines-agents/actions/workflows/verify.yml).

[v0.2.1](https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.1) incluye el caso Patagonia autocontenido y la validación estricta de fechas de caducidad. El ZIP de la release contiene la skill bilingüe completa; los archivos de código fuente de GitHub incluyen también esta presentación y las pruebas.

</details>

---

<p align="center">
  <sub>Un método de <a href="https://www.brthls.com/">Viktor Berthelius</a>. Para leer, utilizar y discutir.</sub><br>
  <sub>MIT para los archivos originales de esta distribución. El manuscrito completo queda fuera. No se conceden derechos sobre marcas de terceros.</sub>
</p>
