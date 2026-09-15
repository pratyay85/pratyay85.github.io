# Pratyay Mukherjee’s academic website

GitHub Pages migration of https://pratyay.net/, preserving the dark green LeanCV-style layout, page addresses, academic content, podcast page, and locally hosted downloadable materials.

**Website:** https://pratyay85.github.io/

## Add the profile photograph

Upload the supplied photograph as **assets/profile.png**. The shared layout detects that file automatically on the next GitHub Pages build. Until the photograph is uploaded, a PM monogram is shown. The old WordPress photograph is not used.

## Edit the website

Edit the HTML below the YAML header in these files directly on GitHub:

| Page | File |
|---|---|
| Home | index.html |
| Publications | research/index.html |
| Teaching | teaching-2/index.html |
| Mentoring | mentoring/index.html |
| Miscellaneous | others/index.html |
| The Coffee House Experience | others/the-coffee-house-experience/index.html |

Shared layout: _layouts/default.html. Navigation: _data/navigation.yml. Appearance: assets/style.css.

GitHub Pages builds the site with Jekyll when changes are pushed to main. In repository Settings → Pages, use **Deploy from a branch → main → /(root)**.

## Downloadable materials

WordPress-hosted files are stored under wp-content/uploads/ with the original paths. Paper links to ePrint, publishers, and other external sites remain external. No WordPress account or paid hosting is required to serve the migrated pages.

## Migration snapshot

The content/ directory contains the imported content and import report. The import script only updates the snapshot and media; it does not overwrite edited website pages. Its workflow is manual after the initial migration.

The validation workflow builds the site, verifies internal links and content, and checks desktop and mobile layouts.

## Connect pratyay.net later

Follow MIGRATION.md before changing DNS.
