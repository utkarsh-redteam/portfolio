# Technical SEO audit: https://utkarsh-sinha.com

**Site:** Utkarsh Sinha portfolio (QA Automation Architect / AI-driven quality engineering leader, 18+ years)  
**Stack observed:** Static site on GitHub Pages (`server: GitHub.com`, Fastly/`via: 1.1 varnish`). Apex A records are the GitHub Pages IPs `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`. `www` CNAME is `utkarsh-redteam.github.io`.  
**Audit date:** 19 Nov 2026, 18:36–18:42 IST (Asia/Calcutta, UTC+5:30)  
**Method:** Fetch and inspect with curl/Shell only (no site changes). HTML/CSS/JS/PDF parsed locally. DNS via Cloudflare DoH. HTTP→HTTPS checked with `curl --resolve` against the authoritative GitHub Pages IPs (this box’s local DNS maps the domain to `198.18.0.1` and is not trustworthy for HTTP).  
**Lighthouse:** `npx lighthouse@12.6.1`, mobile simulated throttling (150 ms RTT, ~1.6 Mbps), HeadlessChrome 156, axe-core 4.14.1. Run at 19 Nov 2026, 18:42 IST.  
**PageSpeed Insights API (no key):** HTTP 429 — quota exceeded for `pagespeedonline.googleapis.com` (`defaultPerDayPerProject`, `quota_limit_value: 0`). No PSI scores available.  
**Not measured (no access / no crawl API):** Google Search Console, Bing Webmaster, actual SERP positions, or a backlink index. Off-page items below are limited to what is visible on the site and in public DNS.

---

## 1. Current state (measured facts only)

The site is a small, already partly SEO-aware static portfolio: two HTML pages (`/` and `/certificates.html`), plus a résumé PDF. Homepage HTML is **24,553 bytes** (gzip **6,373**), last modified **16 Nov 2026, 21:56:08 UTC** (17 Nov 2026, 03:26 IST). Visible homepage copy is about **1,271 words** — not thin for a one-pager — covering role, metrics, experience (Fidelity, Globant, Microsoft and earlier roles), projects, education, and contact.

**What is already in good shape**

- `https://utkarsh-sinha.com/robots.txt` returns **200** (108 bytes) and is valid: `User-agent: *`, `Allow: /`, `Disallow: /tests/`, `Disallow: /todo.md`, and a sitemap declaration.
- `https://utkarsh-sinha.com/sitemap.xml` returns **200** (313 bytes, valid urlset) and lists exactly two URLs: `/` and `/certificates.html`.
- Homepage has `lang="en"`, a mobile viewport, a unique `<title>` (78 characters), a meta description (177 characters), and a correct absolute canonical `https://utkarsh-sinha.com/`.
- `certificates.html` also has `lang="en"`, viewport, and canonical `https://utkarsh-sinha.com/certificates.html`.
- Unknown paths return a **custom 404** (`404.html`, 1,571 bytes) with HTTP **404**, `<title>404 — Page Not Found | Utkarsh Sinha</title>`, and `noindex`.
- HTTPS works. `www` **301**s to the apex. HTTP on the real GitHub Pages IPs **301**s to `https://utkarsh-sinha.com/`. Gzip is on for HTML/CSS/JS. Responses are HTTP/2.
- Homepage `<h1>` is the name “Utkarsh Sinha” (static in HTML, not typed in by JS). The profile photo has `alt="Utkarsh Sinha"`.
- Lighthouse mobile (homepage only): **Performance 80, Accessibility 93, Best Practices 100, SEO 100**. Core Web Vitals in that run: **LCP 3.8 s**, **CLS 0**, **TBT 0 ms**, **FCP 3.8 s**, **Speed Index 3.8 s**, TTFB (simulated) **450 ms** for the document. Total transferred size **125 KiB** (7 requests).  
  Treat the Lighthouse **SEO 100** as a shallow checklist (title, description, canonical, robots, viewport, crawlable links, image alt). It does not mean Open Graph, structured data, content depth, or off-page work are done.

**Main gaps**

- No Open Graph tags, no Twitter card tags, no `og:image` (confirmed missing on both HTML pages; `/assets/og-image.png` is 404).
- No JSON-LD at all (no `Person`, `WebSite`, or `ProfilePage`; no `sameAs`).
- No GitHub (or other profile) link in contact — only LinkedIn, email, phone, and the PDF. “GitHub” appears only as a “GitHub Actions” skill tag.
- Internal nav on the homepage is **hash-only** (`#about`, `#projects`, …). The only crawlable second page is `certificates.html`. Project cards have **zero links**. There is no blog or case-study URL (`/blog` is 404).
- `certificates.html` is thin: **24 visible words**, no meta description, no `<h1>` (the page title is an `<h2>`), generic image alts (“Certificate 1”…), and **1,659,549 bytes** of certificate images (one JPEG is **716,543 bytes**, 3368×2381, shown as a 220 px thumb). Folder typo: `assets/certfificates/`. Filenames include spaces (`SA RPA.png`, etc.).
- Favicon is only a data-URI SVG in the homepage `<link rel="icon">`. `/favicon.ico`, `/apple-touch-icon.png`, and any web manifest are **404**. `certificates.html` has no icon link at all.
- Google Fonts are render-blocking (Inter 400/500/600/700 + JetBrains Mono 400/500/700/800). Lighthouse attributes **~1,810 ms** potential FCP/LCP savings, mostly to the fonts CSS (~790 ms), and LCP is the hero paragraph (`p.hero-desc`) with **78% render delay** (2,974 ms) after TTFB. Two latin `.woff2` files actually downloaded (**48,432** and **31,340** bytes). Homepage first-party CSS/JS are also listed as render-blocking; `script.js` (2,814 bytes) has no `defer`/`async`.
- The hero profile image is `assets/profile.jpg` (**33,867 bytes**, 600×600) with `loading="lazy"`, no `width`/`height`, no `srcset`, no `fetchpriority`. CSS displays it at **96×96** (Lighthouse measured **90×90** on mobile). It fetched at **Low** priority. Lighthouse: modern format could save ~15 KiB; responsive sizing ~31 KiB.
- All first-party responses use GitHub Pages `cache-control: max-age=600` (10 minutes), including CSS, JS, and images. No `Strict-Transport-Security`, CSP, `X-Content-Type-Options`, `Referrer-Policy`, or `X-Frame-Options`. Apex has **no AAAA** (IPv6) records; `utkarsh-redteam.github.io` does.
- Duplicate 200 URLs (same bytes, canonical present but no redirect): `/` and `/index.html` (24,553 bytes); `/certificates.html` and `/certificates` (4,269 bytes). `/404` and `/404.html` return **200** (same 404 template, still `noindex`).
- Source/dev files are deployed and publicly fetchable: `/README.md` (3,570 bytes, 200), `/package.json` (200), `/package-lock.json` (3,071 bytes, 200), `/playwright.config.ts` (3,374 bytes, 200, `content-type: video/mp2t`), `/tests/portfolio.spec.ts` (10,344 bytes, 200, `video/mp2t`), `/todo.md` (5,689 bytes, 200). Only `/tests/` and `/todo.md` are disallowed in robots.txt; the others can be crawled and indexed. `/todo.md` is an internal enhancement list (still refers to `aiquality.in`; notes GSC/Bing as unchecked as of 18 Oct 2026).
- Sitemap `<lastmod>` is **2026-10-18** on both URLs, stale versus the 16 Nov 2026 `Last-Modified` header. No HTML file or DNS TXT `google-site-verification` was found (DNS TXT is only SPF). An IndexNow key file is present at the site root (expected if IndexNow was configured). No `BingSiteAuth.xml` found.
- PDF résumé at `/assets/UTKARSH_SINHA_18_Years_AI_Expert_Technical_QA_Manager.pdf`: **200**, **323,226 bytes**, 2 pages, PDF 1.7, tagged, not linearized. Indexable (no `X-Robots-Tag`). Document **Title** metadata is “Utkarsh Sinha 18 years Test Architect” (does not match the on-page role). Producer is Enhancv marketing copy. Body text uses the current role title; the PDF cites the site as `www.utkarsh-sinha.com`.
- Accessibility issues that also affect SEO/UX: no `<main>` on the homepage (Lighthouse: “Document does not have a main landmark”); heading skip from `<h2>Certifications & Training</h2>` to `<h4>` (“AI for Leaders”); contrast failures on `.stat-label`, `.terminal-title`, `.edu-date`, and `footer` (`--text-muted: #5c6773` on `#0a0e14` is **3.35:1**, below WCAG AA 4.5:1 for normal text). No `:focus-visible` styles; mobile menu button lacks `aria-expanded`; certificate lightbox has no `role="dialog"` or Escape handler.
- `aiquality.in` is a separate live site (HTTP 200, title “QA to EVALs in 1 Weekend”) and does **not** redirect here. Only relevant because `/todo.md` still discusses it as if it were this site.

---

## 2. Prioritised task list

Each item: what’s wrong (with evidence) → the exact fix.

### Critical

- **Dev/source files are live and partly crawlable.** `/README.md` (3,570 B, 200), `/package.json`, `/package-lock.json` (3,071 B), and `/playwright.config.ts` (3,374 B, served as `video/mp2t`) are **200** and **not** listed in `robots.txt`. `/README.md` opens with the same name + role title as the homepage and can compete in name/role queries. `/todo.md` (5,689 B) and `/tests/portfolio.spec.ts` (10,344 B, `video/mp2t`) are also public (robots disallows them, which does not hide them from browsers or non-compliant crawlers). → Stop deploying these files to GitHub Pages (publish only `index.html`, `certificates.html`, `404.html`, `style.css`, `script.js`, `robots.txt`, `sitemap.xml`, and `assets/`; use a `docs/` publish dir or an Actions build with an allow-list). Until then, add `Disallow` rules for `/README.md`, `/package.json`, `/package-lock.json`, and `/playwright.config.ts`.
- **No Open Graph or Twitter card tags, and no social image.** Both HTML pages have zero `og:*` / `twitter:*` tags; `/assets/og-image.png` is 404. LinkedIn/WhatsApp/X shares will show an unbranded preview (and some link unfurlers use these tags). → Add `og:title`, `og:description`, `og:url`, `og:type` (`website` / `profile`), `og:image` (1200×627, with `og:image:width` / `og:image:height` / `og:image:alt`), `og:locale`, and `twitter:card` (`summary_large_image`) + `twitter:image` on both pages. Reuse the same file for WhatsApp/LinkedIn. Validate with LinkedIn Post Inspector and Facebook Sharing Debugger.
- **No JSON-LD structured data.** Zero `application/ld+json` blocks on either page, so Google has no explicit `Person` / `ProfilePage` / `WebSite` graph or `sameAs` links. → Add a single JSON-LD graph on the homepage: `WebSite` (`url`, `name`, `publisher`) + `ProfilePage` + `Person` (`name`, `url`, `image`, `jobTitle`, `description`, `address`/`homeLocation`, `alumniOf` UT Austin, `worksFor` if you want it public, `knowsAbout`, `email`, `sameAs` to LinkedIn and a GitHub profile once the link exists). Put a matching, shorter `Person` (or `CollectionPage`) block on `certificates.html`. Validate with Google’s Rich Results Test / Schema Markup Validator.

### High

- **Google Search Console and Bing Webmaster are not visibly verified.** No `google-site-verification` meta, no obvious verification HTML file, and DNS TXT has only SPF (`v=spf1 include:spf.efwd.registrar-servers.com ~all`). `/todo.md` still marks GSC and Bing registration as unchecked (as of 18 Oct 2026). An IndexNow key file is already at the site root. → Verify the apex property in GSC (DNS TXT is simplest for GitHub Pages), add the `www` property and a domain property, submit `https://utkarsh-sinha.com/sitemap.xml`, inspect `/` and `/certificates.html`, and request indexing. Import the property into Bing Webmaster (or verify there) and keep IndexNow on for future publishes.
- **LCP/FCP are 3.8 s on mobile Lighthouse, driven by render-blocking Google Fonts.** LCP element is `p.hero-desc` (text), not the photo: TTFB 831 ms (22%), render delay 2,974 ms (78%). Fonts CSS is render-blocking; estimated savings **1,810 ms** (fonts CSS alone ~790 ms). Two latin woff2 files total ~80 KiB of the 125 KiB page. `style.css` and `script.js` are also in the render-blocking insight; `script.js` has no `defer`. → Self-host only the weights actually used (or subset to latin), preload the woff2 files, keep `font-display: swap`, and inline or bundle a critical CSS slice. Add `defer` to `script.js`. Optionally drop one family (e.g. keep Inter, use a system stack for “mono”) to shorten the critical path.
- **`certificates.html` is a poor landing page.** Title is a generic 28-character “Certificates — Utkarsh Sinha”; **no meta description**; no `<h1>`; visible text only **24 words**; alts are “Certificate 1/2/3/4” (only CSM is named); images total **1.58 MiB** (largest: 716,543 B, 3368×2381 JPEG) inside a typo folder `assets/certfificates/` with spaces in filenames; no issuer/date/credential text beside most thumbs; no OG/JSON-LD; no favicon. `/certificates` and `/certificates.html` are identical 200s. → Rewrite as a real page: one `<h1>` (e.g. “Certifications — Utkarsh Sinha, QA Automation Architect”), a 140–160 character meta description, a short intro, and for each credential a name, issuer, date, and descriptive alt. Convert to WebP (or AVIF) and serve ~400 px thumbs with `width`/`height`; load the full image only in the lightbox. Rename the folder to `assets/certificates/` and remove spaces from filenames (301 or update every reference). Keep the canonical on one URL and, if you can (Cloudflare or similar), 301 the other.
- **Almost no crawlable internal linking or supporting pages.** Homepage nav is hash anchors only; six “Selected Work” cards have **no hrefs**; `/blog` is 404. Google can index the one-pager’s copy, but there are no URLs to rank for queries like “AI test case generation”, “RAG testing”, or “LangGraph QA agent”. → Turn each project into a crawlable case-study URL (problem → approach → stack → measured outcome). Link to them from the cards, the sitemap, and relevant experience bullets. Optionally add a short articles index (LLM/RAG evaluation, AI-agent testing). Add a visible GitHub profile (and repo) link in contact and in `sameAs`.
- **Hero image is lazy, oversized, and JPEG-only.** `assets/profile.jpg` is 600×600 / 33,867 B, displayed at ~96×96 in `.profile-photo`, with `loading="lazy"` and Low network priority (it sits in the hero). No `width`/`height` or `srcset`. → Remove `loading="lazy"`, add `fetchpriority="high"`, `width="96" height="96"` (or the real display size), and a `srcset`/`sizes` of ~192–256 px WebP/AVIF plus a JPEG fallback. Use that same cropped image (or a dedicated 1200×627 frame) for `og:image` if it still looks sharp.
- **Homepage title and meta description will truncate in SERPs.** Title is **78 characters** (“Utkarsh Sinha — QA Automation Architect | AI-Driven Quality Engineering Leader”); description is **177 characters**. → Tighten the title to ~50–60 characters (keep the name + primary role, e.g. “Utkarsh Sinha — QA Automation Architect | AI Test Automation”). Rewrite the description to ~150–160 characters, still including “QA Automation Architect”, “AI test automation”, “18+ years”, and one proof point (70% automation coverage or 40% faster regression).
- **Résumé PDF is indexable with weak/mismatched metadata.** File is 323,226 B, 2 pages, Title = “Utkarsh Sinha 18 years Test Architect”, Producer = Enhancv promotional text, not in the sitemap (good), no `X-Robots-Tag`. It can compete with `/` for name queries. The on-page heading uses “QA Automation Architect”. → Set PDF Title/Author/Subject to the same role wording as the site, strip the Enhancv Producer string, linearize/compress the file, and give it a stable, shorter filename without spaces. Either keep it indexable and consistent, or send `X-Robots-Tag: noindex` (requires a proxy in front of GitHub Pages) / host it so it is `nofollow` from the page if you do not want it in SERPs. Add a visible HTML “Résumé” summary so the HTML page, not the PDF, is the primary result.

### Medium

- **Sitemap `lastmod` is stale (2026-10-18)** while `Last-Modified` on the HTML is 16 Nov 2026. → Set `<lastmod>` from the real publish date on each deploy (YYYY-MM-DD). Keep the sitemap to indexable HTML URLs only (do not add README, PDF, or hashes).
- **Duplicate 200 URLs:** `/index.html` equals `/`; `/certificates` equals `/certificates.html`. Canonicals already point at the preferred URLs. Certificates nav uses `href="index.html"` and `index.html#…`, which advertise the `/index.html` variant. → Point all internal links at `https://utkarsh-sinha.com/` and `/certificates.html` (or the slash-less form — pick one). If you add Cloudflare (or similar), 301 `/index.html` → `/`.
- **Heading hierarchy skip and missing homepage `<main>`.** Lighthouse accessibility failed `heading-order` on the cert cards (`<h2>` then `<h4>AI for Leaders</h4>`). Index has no `<main>` (Lighthouse: “Document does not have a main landmark”); `certificates.html` does. → Wrap homepage content in `<main>`. Use `<h3>` for certificate names (or demote the section heading consistently). Keep a single `<h1>` per page.
- **Contrast failures on muted text.** `--text-muted: #5c6773` on `--bg: #0a0e14` is **3.35:1**. Lighthouse failed `color-contrast` on hero stat labels (“years experience”, “automation coverage”, “production stability”, “engineers mentored”), the terminal title, the UT Austin date/GPA line, and the footer quote. → Raise muted text to at least 4.5:1 (e.g. around `#8b949e`, already used as `--text-dim` at 6.29:1).
- **Other accessibility items that affect crawlers and UX.** No skip link; no `:focus-visible`; `#navToggle` has `aria-label` but not `aria-expanded`; certificate lightbox has no `role="dialog"`, no Escape-to-close (script.js only clicks the close button / backdrop), no focus trap. Decorative prompts/icons are not `aria-hidden`. → Add those attributes and keyboard behaviour; hide decorative glyphs from assistive tech.
- **Short cache lifetime on static assets** (`cache-control: max-age=600` on CSS, JS, images, PDF). Lighthouse cache insight: ~35 KiB potential waste on revisit (`profile.jpg`, `style.css`, `script.js`). GitHub Pages cannot set long cache headers itself. → Put Cloudflare (or another CDN) in front and cache hashed static assets for a long `max-age` (e.g. 1 year) with fingerprinting; keep HTML shorter. Add HSTS there too (after confirming the HTTP 301 is solid, which it is on GitHub’s IPs).
- **Favicon / Apple touch icon / manifest missing as real files.** `/favicon.ico` and `/apple-touch-icon.png` are 404 (browsers and some bots request them). Data-URI SVG works in modern browsers on the homepage only. → Add a real `/favicon.ico`, SVG favicon, 180×180 `apple-touch-icon.png`, and optional `theme-color`. Link them on every page, including certificates and 404.
- **Off-page profile links are incomplete.** Contact lists LinkedIn (`https://linkedin.com/in/utkarsh-sinha-automation`) but not GitHub, and this audit did not measure backlinks. → Set the website field on LinkedIn (and GitHub profile) to `https://utkarsh-sinha.com/`. Add the GitHub URL on the page and in `sameAs`. Share the site from those profiles once `og:image` exists. Do not expect ranking movement until GSC shows impressions.
- **Apex has no IPv6 (AAAA) records**; `utkarsh-redteam.github.io` does (`2606:50c0:8000::153` … `8003`). → Add the four GitHub Pages AAAA records on the apex if the DNS host allows it, so IPv6-only clients (and some crawlers) are not left on a fallback path.
- **Public `/todo.md` still treats `aiquality.in` as this site.** `aiquality.in` currently returns 200 as a different site and does not redirect here. → Delete `todo.md` from the published branch. If you still own `aiquality.in` and it should point at this portfolio, 301 it (and any key paths) to `https://utkarsh-sinha.com/` so the two hosts do not split or confuse brand queries.

### Low

- **`/404` and `/404.html` return HTTP 200** with the 404 template (already `noindex`). → Harmless if left; avoid linking to them. A proxy 301 to a genuine 404 is optional.
- **Homepage `<h1>` is name-only; the role is an `<h2>`.** This is reasonable for a personal brand. Optional: “Utkarsh Sinha — QA Automation Architect” in the `h1` if you want the role in the main heading without changing the visual design (visually hidden suffix, or a single composed heading).
- **No `theme-color`, web manifest, `llms.txt`, or `security.txt`.** None are required for SEO. Add `theme-color` with the icon set if you want better mobile-chrome branding.
- **No author/robots meta on the HTML pages** (defaults to `index,follow` — fine). Optional: `<meta name="author" content="Utkarsh Sinha">` and an explicit `index,follow` on the two indexable pages.
- **`lang="en"` rather than `en-IN`.** Acceptable. Use `en-IN` only if you want a regional signal; do not add hreflang for a single-language site.
- **Security headers are absent** (no HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`) — GitHub Pages default. Lighthouse notes “No HSTS header found” and “No CSP found in enforcement mode”. This is not an indexing issue. → Add them if you put a CDN/proxy in front.
- **Phone number and `"status": "open_to_opportunities"`** (next to the current employer name in the hero terminal) are in the public HTML. Not an SEO defect; decide if you want that crawlable. A contact form or booking link can replace the raw `tel:` if spam becomes a problem.
- **B.E. graduation year is still missing** (noted in `/todo.md`). Add it when you have the year, for completeness and consistency with the PDF.
- **PDF still contains a Globant bullet “60% reduction in manual testing effort”** (also on the website experience section). That is consistent across HTML and PDF; only a problem if you no longer want that metric. The older “sidebar still says 60%” issue in `/todo.md` appears to have been updated in the PDF sidebar (the PDF now shows 40% there).
- **Lighthouse SEO 100 can be misleading in stakeholder reports.** Keep using GSC (once verified), the Rich Results Test, and this issue list — not the Lighthouse SEO tile — as the source of truth.

---

## 3. Suggested implementation order

1. Remove or block the deployed repo/dev files, then recrawl/inspect in GSC once verified.  
2. Add JSON-LD, Open Graph/Twitter tags, and a 1200×627 `og:image`; add the GitHub `sameAs` link.  
3. Fix fonts / `defer` / hero image so mobile LCP moves toward ≤2.5 s; re-run Lighthouse.  
4. Rebuild `certificates.html` (copy, `h1`, meta, alts, compressed thumbs, folder/filename cleanup).  
5. Publish at least two or three case-study pages and update the sitemap + internal links.  
6. Tighten title/description, PDF metadata, contrast, landmarks/headings, and (if you add a CDN) cache + HSTS + `/index.html` redirects.

---

## 4. Measurement appendix (homepage Lighthouse mobile, 19 Nov 2026, 18:42 IST)

| Metric / category | Value |
| --- | --- |
| Performance / Accessibility / Best Practices / SEO | 80 / 93 / 100 / 100 |
| FCP / LCP / SI / TTI | 3.8 s / 3.8 s / 3.8 s / 3.8 s |
| TBT / CLS / max potential FID | 0 ms / 0 / 20 ms |
| Document TTFB (simulated) | 450 ms (LCP breakdown: TTFB 831 ms, render delay 2,974 ms) |
| Transfer size / requests | 125 KiB / 7 (document 6.8 KiB, CSS 4.9 KiB, JS 1.2 KiB, fonts 80.4 KiB, image 34.2 KiB; third-party 81.9 KiB) |
| Failed a11y audits | `color-contrast`, `heading-order` (missing `main` landmark reported as informative) |
| PSI API | HTTP 429, no scores |

First-party gzip sizes from curl: HTML 6,373 B, `style.css` 3,224 B, `script.js` 996 B, `profile.jpg` 33,867 B (uncompressed JPEG). Certificate image bytes: 716,543 + 254,071 + 255,140 + 328,081 + 105,714 = 1,659,549.
