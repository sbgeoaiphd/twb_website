# thewirebranch.com

Static site for *The Wire Branch* by S.J. Barrett.

Hosted on GitHub Pages. Push to `main` to deploy.

## Setup

1. Repo: `sbgeoaiphd/twb_website`
2. Settings → Pages → Source: "Deploy from a branch" → `main` → `/ (root)`
3. Custom domain is set via the `CNAME` file (`thewirebranch.com`). GitHub reads this on deploy.
4. In the domain registrar, add these DNS records for the apex (`thewirebranch.com`):
   - `A` → `185.199.108.153`
   - `A` → `185.199.109.153`
   - `A` → `185.199.110.153`
   - `A` → `185.199.111.153`
   - `CNAME` for `www` → `sbgeoaiphd.github.io`
5. Wait for DNS propagation, then in Settings → Pages enable **Enforce HTTPS** once GitHub provisions the certificate (can take up to 24h).

### Notes from the marenonnostrum.com setup

- The four `A` records are GitHub's fixed Pages IPs; they do not change between projects.
- Do **not** also point the apex at a registrar parking/forwarding record — a stray `A`/`ALIAS`/forwarding rule on the root is what causes the "domain not verified" / cert-stuck problems.
- If the registrar already has old `A` records on the apex (or an `@` forwarding rule), delete them before adding the four above.
- `www` is optional but recommended; the `CNAME` record above lets `www.thewirebranch.com` redirect to the apex.
- "Enforce HTTPS" stays greyed out until the cert is issued. That's normal — check back later, don't keep toggling.
