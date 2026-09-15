# Migration notes

The first deployment uses https://pratyay85.github.io/. The existing WordPress site remains available at its current address.

## Preserved content

- All five main pages and the Coffee House Experience subpage.
- All 43 peer-reviewed publication entries, three preprints, and other research materials as listed on the source site.
- Program committees, organizing service, invited talks, courses, mentoring history, and Bengali writing.
- Original page URLs: /research/, /teaching-2/, /mentoring/, /others/, and /others/the-coffee-house-experience/.
- Downloaded media, PDF files, and PowerPoint slides under their existing /wp-content/uploads/ paths.
- Page content and media, now presented using the Academic Pages template with a compact left author sidebar and light appearance.

The uploaded PM Standard Photo.png is now used as images/pm-standard-photo.png.

The migration preserves the source page content as it stood at import time; it does not update historical affiliations, paper metadata, or third-party links. WordPress account controls, subscriptions, likes, and comment forms are omitted.

## Editing

The HTML page files are the editable source of truth. content/pages.json is a historical import snapshot. Running the importer does not overwrite the page HTML.

## Optional domain migration

1. Review all pages and the profile photograph.
2. In GitHub Settings → Pages, set the custom domain to pratyay.net.
3. Follow GitHub’s current DNS instructions at https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site .
4. Set url in _config.yml to https://pratyay.net and update robots.txt.
5. Wait for DNS and the certificate, then enable Enforce HTTPS.
6. Verify the site and download links before cancelling WordPress hosting.

Do not delete the domain registration. Domain registration and WordPress hosting are separate services.
