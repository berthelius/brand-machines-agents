# Identity pack 0.1

`brand.json` is this implementation's local format. It does not claim compliance with BCP, MRBS or another external standard. The English example is `assets/brand-machines-en/brand.json` relative to the skill directory; the Spanish example remains `assets/brand-machines/brand.json`.

| Field | Content |
|---|---|
| `schema_version` | `"0.1"` |
| `language` | `"es"` or `"en"`; optional, legacy packs default to ES |
| `id`, `name`, `version` | Brand identifier, name and version |
| `sources` | Local sources with `id`, `title`, `path`, `sha256`; optional `valid_until` (YYYY-MM-DD) |
| `layers` | Seven ordered objects: `id` 1–7, canonical `name`, `summary`, `sources` |
| `principles` | `id`, `layer`, `name`, `definition`, `situations`, `tradeoff`, `example`, `counterexample`, `sources` |
| `checks` | Checks implementing a principle in a particular context |

The six fields of an actionable value come from Chapter 11. IDs, references and version metadata are implementation conventions. Layers and principles may lack sources during diagnosis; the Guardian returns `needs_evidence`. An undocumented layer retains its name with an empty `summary`.

Source paths resolve from the `brand.json` directory and must remain inside it. The checker verifies hashes and declared expiry without network access. Read a source before updating its hash with `hashlib.sha256(path.read_bytes()).hexdigest()`. Integrity does not establish truth or support for a particular claim.

## Language

`--language en` or `--language es` selects the reference identity and its checks; it does not translate content or detect languages. Omitting the flag preserves the Spanish default. With `--pack`, the pack's declared language governs; an explicitly conflicting flag is rejected. English canonical names are Core, Mind, Body, Skin, Engines, Brand OS and Interconnections in that order. Do not mix Spanish and English names within one pack.

Rule IDs, JSON keys, statuses and exit codes are shared across languages. Messages, sources and layer names are localized. An input may declare `language`; if present, it must match the pack. Otherwise, the caller must select the right language; the checker does not guess. Review mixed-language content separately with the relevant pack for each language.

`serve --language en` starts the same local API with the English pack for every request; there is no HTTP language negotiation. Restart the server to change language. Validation errors are localized; native OS errors and standard argparse messages retain the environment's language.

## Supported checks

Every check contains `id`, `kind`, `principle`, `contexts`, `message` and `suggestion`. `contexts` lists exact applicable contexts; `"*"` applies to all. Each check inherits its layer and sources from its principle.

- `forbidden_terms`: adds `terms`, a list of case-insensitive literal matches with word boundaries. It does not interpret negation, quotations or new superlatives.
- `max_exclamations`: adds `maximum`, an integer from 0 to 100. Counts `¡` and `!`.
- `canonical_layers`: compares the input's optional structured `layers` field with the seven layers for the pack's language. It does not extract taxonomies from free prose.

Lexical checks are signals for contextual review. They are not a universal grammar and do not replace Guardian judgment. Rule IDs such as `no_superlativos` remain stable, as in the English book's Chapter 17 example.

## Input piece

```json
{
  "type": "copy",
  "context": "email_subject",
  "language": "en",
  "content": "The BEST offer of the year!!!!"
}
```

Optional `claims` contains objects `{ "text": "literal passage", "sources": ["source-id"] }`. The claim must appear in the content. Missing, unknown or expired sources produce `needs_evidence`. Empty `claims` does not prove the piece has no claims: the agent must read the entire content. Optional `layers` contains the names of the architecture presented by a piece.

## Output and exit codes

`review` returns `revise` for detected issues, `needs_evidence` for missing support, and `needs_review` when executed checks detect no issues. It always preserves `semantic_review: "pending"` and `publication_authorized: false`. If issues and missing evidence coexist, it returns `revise` and retains both lists. `language` identifies the selected pack language.

Exit 0: command completed without detected mechanical issues. Exit 1: review found issues or missing evidence. Exit 2: invalid input, pack or file access. Exit 0 from `diagnose` only means the diagnosis was generated; inspect `missing_layers`.

The API returns HTTP 200 for a generated judgment, 400 for invalid data, 413 for excessive size and 415 for a content type other than JSON. It is a local demonstration bound to a known pack, not a production public server or inference service.
