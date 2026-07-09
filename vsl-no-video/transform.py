import re, sys

SRC = "original_raw2.html"
OUT = "index.html"

with open(SRC, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

orig_len = len(html)
log = []

def sub_count(pattern, repl, s, flags=0, label=""):
    new_s, n = re.subn(pattern, repl, s, flags=flags)
    log.append(f"{label}: {n} replacement(s)")
    return new_s

# 1. Strip SingleFile header comment (reveals original URL)
html = sub_count(
    r"<!--\s*Page saved with SingleFile.*?-->",
    "<!-- Clean Sweets - no-video VSL variant -->",
    html, flags=re.S, label="singlefile_header_comment"
)

# 2a. Remove the base64 GTM bootstrap script (immediately precedes the plain gtag() config block)
html = sub_count(
    r'<script async src="data:application/javascript;base64,[A-Za-z0-9+/=]+"></script>\s*'
    r'(?=<script>\s*window\.dataLayer)',
    "",
    html, flags=re.S, label="gtm_base64_bootstrap"
)

# 2b. Remove explicit gtag() config block (G-C9EVJFDRW8) - plain text, easy match
html = sub_count(
    r"<script>\s*window\.dataLayer.*?gtag\('config', 'G-C9EVJFDRW8'\);\s*</script>",
    "<!-- competitor GA/GTM removed -->",
    html, flags=re.S, label="ga_gtag_block"
)

# 3. Remove image-beacon tracker pinging panaderiacero.com
html = sub_count(
    r"<script>\s*\(function \(\) \{\s*var img = new Image\(\);\s*"
    r'img\.src = "https://panaderiacero\.com[^"]*";\s*\}\)\(\);\s*</script>',
    "<!-- competitor beacon removed -->",
    html, flags=re.S, label="img_beacon"
)

# 3b. Remove Cloudflare Web Analytics beacon scripts (competitor's Cloudflare RUM site tokens)
html = sub_count(
    r"<script defer data-cf-beacon='[^']*'[^>]*></script>",
    "",
    html, label="cloudflare_beacon"
)

# 4. Remove the CSP meta tag single-file injects (blocks our scripts)
html = sub_count(
    r"<meta http-equiv=content-security-policy[^>]*>",
    "",
    html, label="csp_meta"
)

# 5. Remove canonical link pointing at original domain
html = sub_count(
    r"<link rel=canonical href=https://recetas\.panaderiacero\.com/[^>]*>",
    "",
    html, label="canonical_link"
)

# 6. Remove original UTMify (their own pixel ID) - both the base64 loader script and the pixelId block
html = sub_count(
    r'<script data-utmify-prevent-subids async defer src=data:text/javascript;base64,[^>]*></script>',
    "",
    html, label="original_utmify_loader"
)

html = sub_count(
    r'<script>\s*window\.pixelId = "69d1f0601a421f920d2bd295";.*?document\.head\.appendChild\(a\);\s*</script>',
    "",
    html, flags=re.S, label="original_utmify_pixelid_block"
)

# 7. Insert OUR UTMify (real id from our approved VSL) right before </head>
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

# 8. Our Meta pixel (same placeholder pattern as approved vsl/index.html - real ID not found anywhere in project, see report)
our_meta_pixel = (
    "<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
    "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
    "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
    "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}"
    "(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
    "fbq('init', 'META_PIXEL_ID_TODO');fbq('track', 'PageView');</script>\n"
)

if "</head>" in html:
    html = html.replace("</head>", our_meta_pixel + our_utmify + "</head>", 1)
    log.append("inserted_our_meta_pixel_and_utmify: 1")
else:
    log.append("inserted_our_meta_pixel_and_utmify: 0 (NO </head> FOUND)")

# 9. Replace checkout link (competitor off code -> ours, full href copied from vsl/index.html)
old_href = ('href="https://pay.hotmart.com/P104899219T?off=5qdblm2e&amp;utm_source=organic&amp;'
            'utm_campaign=&amp;utm_medium=&amp;utm_content=&amp;utm_term=&amp;'
            'xcod=jLj6a4fbafbbf6bf53ca56273d0hQwK21wXxRhQwK21wXxRhQwK21wXxRhQwK21wXxR&amp;'
            'sck=jLj6a4fbafbbf6bf53ca56273d0hQwK21wXxRhQwK21wXxRhQwK21wXxRhQwK21wXxR"')
new_href = ('href="https://pay.hotmart.com/P104899219T?off=5tpbk1a1&amp;utm_source=organic&amp;'
            'utm_campaign=&amp;utm_medium=&amp;utm_content=&amp;utm_term=&amp;'
            'xcod=jLj6a4d14b65c30c3222e5931d8hQwK21wXxRhQwK21wXxRhQwK21wXxRhQwK21wXxR&amp;'
            'sck=jLj6a4d14b65c30c3222e5931d8hQwK21wXxRhQwK21wXxRhQwK21wXxRhQwK21wXxR"')
n = html.count(old_href)
html = html.replace(old_href, new_href)
log.append(f"checkout_link_replaced: {n}")

# 10. Title
html = sub_count(
    r"<title>Clean Sweets - Eat Desserts Without Guilt</title>",
    "<title>Clean Sweets — Eat Desserts Without Guilt</title>",
    html, label="title"
)

# 11. Add meta description (none existed)
html = html.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<meta name="description" content="Clean Sweets - Eat Desserts Without Guilt. Sugar-free, diabetic-friendly dessert recipes.">',
    1
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("ORIG LEN:", orig_len, "NEW LEN:", len(html))
for l in log:
    print(l)
