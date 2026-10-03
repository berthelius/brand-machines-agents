# Contributing

Open a focused pull request describing the problem, resulting behavior and validation. Fixes, sourced worked examples and language improvements are useful contributions.

Preserve the seven canonical layers and their meaning. Keep each brand's identity, principles and sources separate; the Brand Machines reference identity is not a universal aesthetic. Read the [method](skills/brand-machines/references/en/method.md) and [pack format](skills/brand-machines/references/en/pack.md) before changing a pack.

For a case study, link primary sources with consultation dates and distinguish observed facts, analyst inferences and hypothetical messages. Leave unsupported layers empty. Summarize sources in original words, respect third-party rights, and disclose any relationship with the subject. A file hash proves integrity, not truth. Re-read a changed note before updating its hash.

Separate mechanical output from semantic judgment. Report only checks actually run; do not turn curated fixtures into accuracy claims or invent commercial results. State model involvement and whether a reviewer also wrote the cases. Keep examples and their sources inside the skill directory so installation remains self-contained.

Use the existing checker and Python standard library where possible. Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 skills/brand-machines/scripts/bm.py validate
python3 skills/brand-machines/scripts/bm.py validate --language en
python3 skills/brand-machines/assets/case-studies/patagonia/run.py
```

CI runs on Python 3.10, 3.12 and 3.14. Update both top-level READMEs when changing public usage. A passing suite does not authorize publication or certify semantic coherence.
