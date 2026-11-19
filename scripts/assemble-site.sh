#!/usr/bin/env bash
# Copy the public site into _site/. GitHub Pages should publish this directory
# via Actions, not the repository root. Dev files stay in git and are omitted here.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
dest="$root/_site"

rm -rf "$dest"
mkdir -p "$dest"

copy() {
  local rel="$1"
  if [[ ! -e "$root/$rel" ]]; then
    echo "missing site file: $rel" >&2
    exit 1
  fi
  mkdir -p "$dest/$(dirname "$rel")"
  cp -a "$root/$rel" "$dest/$rel"
}

files=(
  index.html
  certificates.html
  404.html
  style.css
  script.js
  robots.txt
  sitemap.xml
  CNAME
  .nojekyll
  favicon.svg
  favicon.ico
  apple-touch-icon.png
  icon-192.png
  icon-512.png
  site.webmanifest
  llms.txt
  .well-known/security.txt
  da9cf99a18684365be085cc63a65a99d.txt
  assets/profile.jpg
  assets/profile-96.webp
  assets/profile-192.webp
  assets/profile-288.webp
  assets/profile-192.jpg
  assets/og-image.png
  assets/UTKARSH_SINHA_18_Years_AI_Expert_Technical_QA_Manager.pdf
)

for rel in "${files[@]}"; do
  copy "$rel"
done

mkdir -p "$dest/fonts" "$dest/assets/certificates" "$dest/work"
cp -a "$root"/fonts/*.woff2 "$dest/fonts/"
cp -a "$root"/fonts/OFL-Inter.txt "$root"/fonts/OFL-JetBrainsMono.txt "$dest/fonts/"
cp -a "$root"/assets/certificates/*.webp "$dest/assets/certificates/"
cp -a "$root"/work/*.html "$dest/work/"

# Backstop: these must never be in the published tree.
forbidden=(
  README.md
  package.json
  package-lock.json
  playwright.config.ts
  todo.md
  "MASTER TODO.md"
  seo-tracker.html
  seo-audit-utkarsh-sinha.md
  commitNpush.bat
  runAndPush.bat
  assets/applyJob.md
  assets/og-image.svg
)
for rel in "${forbidden[@]}"; do
  if [[ -e "$dest/$rel" ]]; then
    echo "refusing to publish $rel" >&2
    exit 1
  fi
done

if [[ -d "$dest/tests" || -d "$dest/scripts" || -d "$dest/workflows" || -d "$dest/assets/certfificates" ]]; then
  echo "refusing to publish a dev or legacy directory" >&2
  exit 1
fi

if [[ ! -s "$dest/CNAME" || ! -s "$dest/assets/og-image.png" || ! -s "$dest/404.html" ]]; then
  echo "published site is missing CNAME, og-image, or 404.html" >&2
  exit 1
fi

python3 - "$dest" <<'PY'
import sys
from pathlib import Path
root = Path(sys.argv[1])
bad = []
for path in root.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() in {".html", ".css", ".js", ".xml", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text or "certfificates" in text:
            bad.append(str(path))
if bad:
    print("published files still reference Google Fonts or the old certificate folder:")
    print("\n".join(bad))
    sys.exit(1)
print(f"assembled {sum(1 for p in root.rglob('*') if p.is_file())} files")
PY
