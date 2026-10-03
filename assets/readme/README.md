# README artwork

`fig-hero-agent-edition.svg` is original artwork for the agent edition. The seven connected strata follow the book's architecture; the red foundation represents the Core. It uses the project's paper, ink and single accent (`#fafafa`, `#1A1A1A`, `#e63946`), with `#666666` for secondary text. Typography: EB Garamond, Source Sans 3 and Source Code Pro.

The visible SVG has outlined lettering so GitHub readers do not need those fonts installed. Its editable source is `fig-hero-agent-edition-source.svg`. With the three fonts and Inkscape installed, regenerate from the repository root:

```sh
inkscape assets/readme/fig-hero-agent-edition-source.svg \
  --export-text-to-path --export-plain-svg \
  --export-filename=assets/readme/fig-hero-agent-edition.svg
```

The light paper surface is intentional in both GitHub themes. Each README supplies localized alternative text, and the seven layer names remain selectable text in its method table. This is a digital title graphic, not a replacement for a plate in the printed book.

`cover-es.webp` and `cover-en.webp` are the existing approved marketing covers, copied unchanged from [the book's Spanish site](https://machines.brthls.com/) and [English site](https://machines.brthls.com/en/). No manuscript pages are included. The original source URLs are `/assets/cover-es.webp` and `/assets/cover-en.webp` on that domain.
