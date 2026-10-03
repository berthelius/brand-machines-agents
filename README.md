<p align="center"><strong>English</strong> · <a href="README.es.md" lang="es">Español</a></p>

<h1 align="center">Brand Machines</h1>

<p align="center"><strong>The method for agents.</strong></p>

<p align="center">
  Diagnose, design and review brand systems.<br>
  Seven layers, decision principles and verifiable sources.<br>
  <sub>A method by Viktor Berthelius.</sub>
</p>

<p align="center">
  <a href="https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.0"><img src="https://img.shields.io/badge/v0.2.0-e63946?style=flat-square" alt="Version 0.2.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-1a1a1a?style=flat-square" alt="MIT license"></a>
  <a href="#the-guardian-in-action"><img src="https://img.shields.io/badge/Python-3.10%2B-1a1a1a?style=flat-square" alt="Local checker: Python 3.10 or later"></a>
</p>

<p align="center">
  <a href="#install"><strong>Install</strong></a> ·
  <a href="skills/brand-machines/assets/case-studies/patagonia/README.md">Patagonia case</a> ·
  <a href="#three-ways-to-work">Use</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="https://machines.brthls.com/en/">The book and the system</a>
</p>

---

<p align="center">
  <strong>Core · Mind · Body · Skin</strong><br>
  <strong>Engines · Brand OS · Interconnections</strong>
</p>

> The method is shared. Each brand has its own identity.

This skill adapts *Brand Machines: A General Theory of Brand Systems* to an agent's work. The included reference identity describes Brand Machines; its sources, style and decisions are not imposed on other brands. English terminology follows the published book's canon and glossary.

## Start with a real brand, hypothetical decisions

**[Patagonia: when should a brand recommend buying less?](skills/brand-machines/assets/case-studies/patagonia/README.md)** Four primary sources, five hypothetical messages and a reproducible local check, with a separate annotated semantic review.

“Replace the one that still works” and “consider replacement when required use cannot be restored” lead to different judgments under the same principle. An authentic guarantee also fails to support a promise of free repairs within 48 hours. The case shows the evidence behind each decision and leaves four undocumented layers empty.

An independent educational study, not endorsed by Patagonia. Run the example without an account, API key or book purchase:

```sh
python3 skills/brand-machines/assets/case-studies/patagonia/run.py
```

Run from a clone of this repository. This reproduces mechanical checks; the [annotated review](skills/brand-machines/assets/case-studies/patagonia/semantic-review.md) explains the semantic judgments and their limits.

## Install

Run from the project where you want to use the skill:

```sh
npx skills add berthelius/brand-machines-agents --skill brand-machines
```

**Available in English and Spanish.** Installation verified in **Codex** and **Claude Code**. The installer lets you choose agents and installation scope.

| Agent | Invocation |
| :--- | :--- |
| Codex | `$brand-machines` |
| Claude Code | `/brand-machines` |

<details>
<summary>Manual installation and other agents</summary>

Download the repository or [release](https://github.com/berthelius/brand-machines-agents/releases/tag/v0.2.0). Copy the complete `skills/brand-machines` folder—or `brand-machines` from the ZIP—to your agent's skills directory. Keep `references`, `scripts`, `assets` and `agents` alongside `SKILL.md`.

The documentation works with any agent able to read these files; automatic discovery depends on the environment. Python 3.10 or later is needed only for the optional local checker, which has no external dependencies.

</details>

The agent responds in your language. For the local checker, use `--language en` or `--language es`: it selects that language's identity and rules. Existing commands without a flag still use the Spanish pack. With `--pack`, the pack's language governs.

## Three ways to work

### 01 · Diagnose

> Use Brand Machines to diagnose this brand from the attached documents. Distinguish evidence, inferences and missing information for each layer.

### 02 · Propose

> Apply Brand Machines to this brief. Derive the proposal from our principles, explain the trade-off and identify decisions that still need approval.

### 03 · Review

> Act as Guardian for this proposal. Check its claims against their sources and its decisions against the Core. Allow coherent variation and suggest a correction where needed.

## The Guardian, in action

A demonstration from Chapter 17. After cloning the repository, run from its root:

```sh
python3 skills/brand-machines/scripts/bm.py review --language en \
  --input skills/brand-machines/assets/examples/en/chapter-17.json
```

**Piece:** “The BEST offer of the year!!!!”

**Result:** `revise`, with `no_superlativos` and `exclamaciones_excesivas`, their sources and suggested revisions. Exit code 1 is expected for this example. Rule IDs remain the same in both languages, as in the book.

**The checker applies explicit rules. The agent performs semantic review.** A piece with no mechanical issues returns `needs_review`: its coherence still requires judgment.

<details>
<summary>Validate a pack, diagnose and try a variation</summary>

```sh
python3 skills/brand-machines/scripts/bm.py validate --language en
python3 skills/brand-machines/scripts/bm.py diagnose --language en
python3 skills/brand-machines/scripts/bm.py review --language en \
  --input skills/brand-machines/assets/examples/en/variation.json
```

The variation returns `needs_review`. `assets/examples/en/semantic-contradiction.json` shows why: a decision can pass lexical checks while contradicting the definition of Brand Machine.

`review`, `diagnose`, `validate` and `serve` accept `--pack path/to/brand.json` to use another identity. Select the right language explicitly; the checker does not detect or translate input. For mixed-language material, review each language with its corresponding pack.

</details>

<details>
<summary>Local API · no keys or model calls</summary>

```sh
python3 skills/brand-machines/scripts/bm.py serve --language en
```

In another terminal:

```sh
curl http://127.0.0.1:8765/api/v1/validate \
  -H 'Content-Type: application/json' \
  --data '{"type":"copy","language":"en","content":"The BEST offer of the year!!!!","context":"email_subject"}'
```

The API runs the same checker and listens only on your machine, using the pack selected at startup for all requests. It needs no keys, makes no model calls and publishes nothing. It is not a hosted public service.

</details>

<details>
<summary>What each check establishes</summary>

| Part | Establishes | Does not establish |
| :--- | :--- | :--- |
| `validate` | Pack structure and source integrity | Truth of the sources |
| `diagnose` | Documentation coverage by layer | Brand maturity |
| `review` / API | Declared checks and presence/expiry of references | Complete semantic coherence or truth of claims |
| Skill applied by an agent | A reasoned review within available scope and sources | Automatic permission to publish |

</details>

## Documentation

| Reference | Content |
| :--- | :--- |
| [Method](skills/brand-machines/references/en/method.md) | The seven layers and their relationships. |
| [Workflows](skills/brand-machines/references/en/workflows.md) | Diagnosis, proposal and review. |
| [Guardian contract](skills/brand-machines/references/en/review.md) | Criteria, findings and scope of review. |
| [Pack format](skills/brand-machines/references/en/pack.md) | Representing another identity and its sources. |
| [Editorial provenance](skills/brand-machines/references/provenance.json) | Sources of this adaptation and English terminology. |
| [Patagonia worked case](skills/brand-machines/assets/case-studies/patagonia/README.md) | Public sources, five scenarios, observed checks and scoped semantic judgments. |
| [Contributing](CONTRIBUTING.md) | Evidence, brand separation and validation requirements. |

<details>
<summary>Development and tests</summary>

```sh
python3 -m unittest discover -s tests -v
python3 skills/brand-machines/assets/case-studies/patagonia/run.py
```

Automated tests cover the local code in both languages, language boundaries and legacy Spanish packs. Scenarios in the [Guardian contract](skills/brand-machines/references/en/review.md) separately evaluate agent behavior. A passing mechanical suite does not establish semantic correctness. [View CI](https://github.com/berthelius/brand-machines-agents/actions/workflows/verify.yml).

</details>

The latest tagged release is v0.2.0. This source tree also includes the Patagonia study and stricter source-expiry validation; those additions are not in the v0.2.0 release archive. The skill remains self-contained and the local checker has no external dependencies.

---

<p align="center">
  <strong>Brand Machines</strong><br>
  <sub>A General Theory of Brand Systems · Viktor Berthelius</sub><br><br>
  <a href="https://machines.brthls.com/en/#book">The book</a> ·
  <a href="https://machines.brthls.com/en/">machines.brthls.com</a> ·
  <a href="https://www.brthls.com/en/">brthls.com</a>
</p>

<p align="center"><sub>MIT for this distribution's files. The complete manuscript and its private editorial repository are not included. No rights to third-party brands are granted.</sub></p>
