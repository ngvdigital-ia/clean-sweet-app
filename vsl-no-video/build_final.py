import re

with open("raw_curl.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

log = []
def sub1(pattern, repl, s, flags=0, label=""):
    new_s, n = re.subn(pattern, repl, s, count=1, flags=flags)
    log.append(f"{label}: {n}")
    return new_s

# 1. Title with em dash as requested
html = sub1(r"<title>Clean Sweets - Eat Desserts Without Guilt</title>",
            "<title>Clean Sweets — Eat Desserts Without Guilt</title>",
            html, label="title")

# 2. Add meta description + dns-prefetch (performance) right after viewport meta
extra_head = (
    '<meta name="description" content="Clean Sweets - Eat Desserts Without Guilt. '
    'Sugar-free, diabetic-friendly dessert recipes.">\n'
    '    <link rel="dns-prefetch" href="//cdn.utmify.com.br">\n'
    '    <link rel="dns-prefetch" href="//connect.facebook.net">\n'
    '    <link rel="dns-prefetch" href="//fonts.googleapis.com">\n'
    '    <link rel="dns-prefetch" href="//fonts.gstatic.com">'
)
html = sub1(r'<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    ' + extra_head,
            html, label="meta_description_dns_prefetch")

# 3. Make Google Fonts non-blocking (preload + swap pattern) instead of a blocking stylesheet
old_fonts = ('<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&amp;'
             'family=Open+Sans:wght@400;600;700&amp;display=swap" rel="stylesheet">')
new_fonts = (
    '<link rel="preload" as="style" '
    'href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&amp;'
    'family=Open+Sans:wght@400;600;700&amp;display=swap" '
    'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
    '    <noscript><link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&amp;'
    'family=Open+Sans:wght@400;600;700&amp;display=swap"></noscript>'
)
html = sub1(re.escape(old_fonts), new_fonts, html, label="fonts_nonblocking")

# 4. Localize all image references (panaderiacero.com -> local /images/*.webp)
image_map = {
    "https://panaderiacero.com/wp-content/uploads/2026/03/f4.png": "images/f4.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/f1.jpg": "images/f1.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/f2.jpg": "images/f2.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/f3.png": "images/f3.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/4.jpg": "images/4.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/11111.jpg": "images/11111.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/2.jpg": "images/2.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/3.jpg": "images/3.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/7.jpg": "images/7.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/5.jpg": "images/5.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/6.jpg": "images/6.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/CELULAR.png": "images/CELULAR.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/tes1.jpg": "images/tes1.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/tes2.jpg": "images/tes2.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/02/tes3.jpg": "images/tes3.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/B1.png": "images/B1.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/B2.png": "images/B2.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/B33.png": "images/B33.webp",
    "https://panaderiacero.com/wp-content/uploads/2026/03/7-days.png": "images/7-days.webp",
}
total_img_repl = 0
for old, new in image_map.items():
    n = html.count(old)
    html = html.replace(old, new)
    total_img_repl += n
log.append(f"image_localization: {total_img_repl} total replacements across {len(image_map)} unique URLs")

# 5. Remove original UTMify block (their pixel id 69d1f0601a421f920d2bd295)
html = sub1(
    r'<script src="https://cdn\.utmify\.com\.br/scripts/utms/latest\.js" data-utmify-prevent-subids="" async="" defer=""></script>\s*'
    r'<!-- Utmify Pixel -->\s*'
    r'<script>\s*window\.pixelId = "69d1f0601a421f920d2bd295";.*?document\.head\.appendChild\(a\);\s*</script>',
    "<!-- competitor UTMify removed -->",
    html, flags=re.S, label="original_utmify"
)

# 6. Remove Google Analytics (GA4) block
html = sub1(
    r'<!-- Google Analytics \(GA4\) -->\s*'
    r'<script async="" src="https://www\.googletagmanager\.com/gtag/js\?id=G-C9EVJFDRW8"></script>\s*'
    r'<script>\s*window\.dataLayer = window\.dataLayer \|\| \[\];\s*'
    r"function gtag\(\)\{dataLayer\.push\(arguments\);\}\s*"
    r"gtag\('js', new Date\(\)\);\s*"
    r"gtag\('config', 'G-C9EVJFDRW8'\);\s*</script>\s*"
    r"<!-- End Google Analytics \(GA4\) -->",
    "<!-- competitor GA/GTM removed -->",
    html, flags=re.S, label="ga_block"
)

# 7. Remove image-beacon tracker
html = sub1(
    r"<script>\s*\(function \(\) \{\s*var img = new Image\(\);\s*"
    r'img\.src = "https://panaderiacero\.com/new/clean-sweets-tsl/";\s*\}\)\(\);\s*</script>',
    "<!-- competitor beacon removed -->",
    html, flags=re.S, label="img_beacon"
)

# 8. Insert OUR Meta pixel + OUR UTMify (same as approved vsl/index.html) before </head>
our_meta_pixel = (
    "<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
    "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
    "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
    "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}"
    "(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
    "fbq('init', 'META_PIXEL_ID_TODO');fbq('track', 'PageView');</script>\n"
)
our_utmify = (
    '<script>\n'
    '  window.pixelId = "69b4c941c50ca6489c210ca6";\n'
    '  var a = document.createElement("script");\n'
    '  a.setAttribute("async", "");\n'
    '  a.setAttribute("defer", "");\n'
    '  a.setAttribute("src", "https://cdn.utmify.com.br/scripts/pixel/pixel.js");\n'
    '  document.head.appendChild(a);\n'
    '</script>\n'
)
n = html.count("</head>")
html = html.replace("</head>", our_meta_pixel + our_utmify + "</head>", 1)
log.append(f"insert_our_pixels: {n} </head> found, inserted once")

# 9. Checkout link: swap off code to ours (surgical, minimal change)
n = html.count('href="https://pay.hotmart.com/P104899219T?off=5qdblm2e" class="cta-btn"')
html = html.replace(
    'href="https://pay.hotmart.com/P104899219T?off=5qdblm2e" class="cta-btn"',
    'href="https://pay.hotmart.com/P104899219T?off=5tpbk1a1" class="cta-btn"'
)
log.append(f"checkout_link: {n}")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("FINAL LEN:", len(html))
for l in log:
    print(l)
