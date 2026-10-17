"""Builds the public website in docs/ from src/game.html.

src/game.html is the single source of the game (it also runs as a Claude artifact).
This script wraps it in a full HTML document with SEO tags, self-hosted fonts,
an installable web-app manifest and an offline service worker.
"""
import json, os, re, hashlib, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE_URL = os.environ.get('SITE_URL', 'https://merterden-sw.github.io/yesim-mahjong/')
DOCS = os.path.join(ROOT, 'docs')

src = open(os.path.join(ROOT, 'src', 'game.html'), encoding='utf-8').read()

# Drop the artifact-only head lines and the Google Fonts links; the site serves its own fonts.
body = re.sub(r'^(<meta[^>]*>\n|<title>.*?</title>\n|<link rel="(?:preconnect|stylesheet)"[^>]*>\n)+', '', src)
assert '<style>' in body[:200], 'unexpected start of game.html'
body = body.replace('<!--SITE_LINKS-->',
    '<p class="site-links"><a href="gizlilik.html" target="_blank" rel="noopener">Gizlilik / Privacy</a>'
    '<a href="https://github.com/Merterden-sw/yesim-mahjong/issues" target="_blank" rel="noopener">Geri bildirim / Feedback</a></p>')

title = 'Yeşim Mahjong'
desc = ('Ücretsiz Mahjong Solitaire: büyük, okunaklı taşlar, rahat mod, günlük görevler ve sınırsız seviye. '
        'Reklamsız, kayıt gerektirmez, tarayıcıda oynanır.')
desc_en = 'Free Mahjong Solitaire with big, easy-to-read tiles, a relaxed mode, daily tasks and endless levels. No ads, no sign-up.'
ld = {
    '@context': 'https://schema.org', '@type': 'VideoGame', 'name': title, 'url': SITE_URL,
    'description': desc_en, 'genre': ['Puzzle', 'Mahjong Solitaire'], 'gamePlatform': ['Web browser', 'Android', 'iOS'],
    'applicationCategory': 'Game', 'operatingSystem': 'Any', 'inLanguage': ['tr', 'en'],
    'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'TRY'},
    'image': SITE_URL + 'og.jpg',
}
head = f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} – Ücretsiz Mahjong Solitaire</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE_URL}">
<meta name="theme-color" content="#0f3b35">
<meta name="color-scheme" content="dark">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{title}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{title}">
<meta property="og:title" content="{title} – Ücretsiz Mahjong Solitaire">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="tr_TR">
<meta property="og:locale:alternate" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE_URL}og.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="preload" href="fonts/fonts.css" as="style">
<link rel="stylesheet" href="fonts/fonts.css">
<style>html {{ box-sizing: border-box; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); background: #0f3b35; }}</style>
<noscript><style>.app {{ display: none; }}</style></noscript>
</head>
<body>
<noscript><p style="color:#f3efe2;font:18px system-ui;padding:24px">Yeşim Mahjong için JavaScript gerekli. / Yeşim Mahjong needs JavaScript.</p></noscript>
'''
tail = '''
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
</script>
</body>
</html>
'''
open(os.path.join(DOCS, 'index.html'), 'w', encoding='utf-8').write(head + body + tail)

manifest = {
    'name': title, 'short_name': 'Mahjong', 'lang': 'tr', 'dir': 'ltr',
    'description': desc, 'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'any',
    'background_color': '#0f3b35', 'theme_color': '#0f3b35', 'categories': ['games', 'entertainment'],
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}
json.dump(manifest, open(os.path.join(DOCS, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# Offline support: precache every file the game needs. The cache name changes whenever any of them changes.
assets = ['./', 'index.html', 'manifest.webmanifest', 'fonts/fonts.css'] + \
    ['fonts/' + f for f in sorted(os.listdir(os.path.join(DOCS, 'fonts'))) if f.endswith('.woff2')] + \
    ['icons/' + f for f in ('icon-192.png', 'icon-512.png', 'favicon-32.png', 'apple-touch-icon.png')]
h = hashlib.sha1()
for a in assets[1:]:
    h.update(open(os.path.join(DOCS, a), 'rb').read())
version = h.hexdigest()[:12]
sw = f'''// Generated by tools/build.py. Precaches the game so it works offline.
const CACHE = 'yesim-{version}';
const ASSETS = {json.dumps(assets)};
self.addEventListener('install', (e) => {{
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', (e) => {{
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', (e) => {{
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  // Pages: network first so updates show up, cache when offline. Everything else: cache first.
  if (req.mode === 'navigate') {{
    e.respondWith(fetch(req).then((res) => {{ const copy = res.clone(); caches.open(CACHE).then((c) => c.put('index.html', copy)); return res; }})
      .catch(() => caches.match('index.html')));
    return;
  }}
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req)));
}});
'''
open(os.path.join(DOCS, 'sw.js'), 'w', encoding='utf-8').write(sw)

today = datetime.date.today().isoformat()
open(os.path.join(DOCS, 'sitemap.xml'), 'w').write(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE_URL}</loc><lastmod>{today}</lastmod></url>\n  <url><loc>{SITE_URL}gizlilik.html</loc><lastmod>{today}</lastmod></url>\n</urlset>\n')
open(os.path.join(DOCS, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n')
open(os.path.join(DOCS, '.nojekyll'), 'w').write('')
print('built', SITE_URL, 'cache', version)
