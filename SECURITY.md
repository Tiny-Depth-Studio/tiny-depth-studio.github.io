# Security

Found a security problem in this site, one of the game sites, or one of our games?
Email **tinydepthstudio@gmail.com** with the details and, if you can, the steps to
reproduce it. Please do not open a public issue for it. We reply within a few days.

## How this site is built

- Static HTML on GitHub Pages, served over HTTPS only (Settings -> Pages -> Enforce HTTPS).
- No JavaScript, no cookies, no forms, no third-party requests: the Content-Security-Policy
  in every page allows only the stylesheet and images from this origin
  (`default-src 'none'; img-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'`).
- Store data and artwork are fetched from Steam at build time by a GitHub Actions workflow,
  never by the visitor's browser. Images are accepted only from Steam's CDN over HTTPS,
  only as JPEG or PNG, and only up to 3 MB.
- Workflow actions are pinned to commit SHAs and the workflow token has `contents: write`
  only. Dependabot proposes action updates monthly.
