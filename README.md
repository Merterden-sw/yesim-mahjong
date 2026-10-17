# Yeşim Mahjong

Büyük, okunaklı taşlarla tarayıcıda oynanan ücretsiz Mahjong Solitaire.

**Oyna:** https://merterden-sw.github.io/yesim-mahjong/

- 12 elle tasarlanmış dizilim, 13. seviyeden sonra her oyuncuda aynı olan sınırsız üretilmiş seviye
- Her dağıtım çözülebilir; karıştırma da çözülebilir kalır
- 1–3 yıldız, günlük görevler ve seri sayacı
- Rahat mod (süre tutulmaz), Türkçe ve İngilizce
- Çevrimdışı çalışır, ana ekrana eklenebilir (PWA)
- Reklam, çerez ve analiz aracı yok; ilerleme cihazda saklanır, yedek koduyla taşınır

## Klasörler

| Yol | Ne var |
|---|---|
| `src/game.html` | Oyunun tek kaynak dosyası (Claude artifact olarak da çalışır) |
| `docs/` | Yayınlanan site (GitHub Pages bu klasörü sunar) |
| `tools/build.py` | `src/game.html` dosyasından `docs/index.html`, manifest, service worker ve site haritasını üretir |
| `tools/make_icons.py` | Uygulama ikonlarını çizer |
| `tools/shots.mjs`, `tools/promo.html` | Portal kapaklarını ve mağaza ekran görüntülerini headless Chrome ile çeker |
| `release/` | Portal metinleri, görseller ve yükleme paketi |

## Güncelleme

```bash
python3 tools/build.py
```

Görselleri yenilemek için önce `docs/` klasörünü yerelde sun (`python3 -m http.server 4460 --directory docs`), sonra:

```bash
node tools/shots.mjs http://localhost:4460/
```

`docs/` klasörüne yapılan her push siteyi birkaç dakika içinde günceller.

## Lisans

Kod ve görseller: © 2026 Selahattin Mert Erden. Tüm hakları saklıdır. Kaynak kodun burada görünür olması kullanım izni vermez.

Yazı tipleri: [Lexend](https://fonts.google.com/specimen/Lexend) ve [Noto Serif TC](https://fonts.google.com/noto/specimen/Noto+Serif+TC), SIL Open Font License 1.1.
