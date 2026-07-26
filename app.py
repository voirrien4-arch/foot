from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess, os, re, requests, sys, shutil
from datetime import datetime

app = Flask(__name__)
CORS(app)

SITES_META = {
    "github.com":        {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Plateforme de code source et projets open-source"},
    "twitter.com":       {"category": "Réseau social",   "country": "US", "lang": "EN", "desc": "Réseau social de microblogging"},
    "x.com":             {"category": "Réseau social",   "country": "US", "lang": "EN", "desc": "Anciennement Twitter, réseau social"},
    "instagram.com":     {"category": "Réseau social",   "country": "US", "lang": "EN", "desc": "Partage de photos et vidéos"},
    "facebook.com":      {"category": "Réseau social",   "country": "US", "lang": "EN", "desc": "Réseau social généraliste"},
    "linkedin.com":      {"category": "Professionnel",   "country": "US", "lang": "EN", "desc": "Réseau social professionnel"},
    "reddit.com":        {"category": "Forum",            "country": "US", "lang": "EN", "desc": "Plateforme de discussion communautaire"},
    "tiktok.com":        {"category": "Réseau social",   "country": "CN", "lang": "Multi", "desc": "Plateforme de vidéos courtes"},
    "youtube.com":       {"category": "Vidéo",           "country": "US", "lang": "Multi", "desc": "Plateforme de streaming vidéo"},
    "twitch.tv":         {"category": "Streaming",       "country": "US", "lang": "EN", "desc": "Streaming de jeux vidéo en direct"},
    "pinterest.com":     {"category": "Réseau social",   "country": "US", "lang": "Multi", "desc": "Partage visuel et inspiration"},
    "tumblr.com":        {"category": "Blog",             "country": "US", "lang": "EN", "desc": "Plateforme de microblogging créatif"},
    "medium.com":        {"category": "Blog",             "country": "US", "lang": "EN", "desc": "Plateforme de publication d'articles"},
    "patreon.com":       {"category": "Monétisation",    "country": "US", "lang": "EN", "desc": "Plateforme de soutien aux créateurs"},
    "onlyfans.com":      {"category": "Adulte/Créateur", "country": "GB", "lang": "EN", "desc": "Plateforme de contenu exclusif"},
    "snapchat.com":      {"category": "Messagerie",      "country": "US", "lang": "Multi", "desc": "Application de messagerie éphémère"},
    "telegram.org":      {"category": "Messagerie",      "country": "AE", "lang": "Multi", "desc": "Application de messagerie sécurisée"},
    "discord.com":       {"category": "Communauté",      "country": "US", "lang": "Multi", "desc": "Plateforme de discussion communautaire"},
    "steamcommunity.com":{"category": "Gaming",          "country": "US", "lang": "Multi", "desc": "Communauté Steam de jeux vidéo"},
    "roblox.com":        {"category": "Gaming",          "country": "US", "lang": "EN", "desc": "Plateforme de jeux en ligne"},
    "chess.com":         {"category": "Gaming",          "country": "US", "lang": "Multi", "desc": "Plateforme d'échecs en ligne"},
    "hackerrank.com":    {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Plateforme de défis de programmation"},
    "leetcode.com":      {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Préparation aux entretiens techniques"},
    "stackoverflow.com": {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Q&A pour développeurs"},
    "gitlab.com":        {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Plateforme DevOps et code"},
    "bitbucket.org":     {"category": "Développement",   "country": "AU", "lang": "EN", "desc": "Hébergement de code Git"},
    "replit.com":        {"category": "Développement",   "country": "US", "lang": "EN", "desc": "IDE en ligne collaboratif"},
    "codepen.io":        {"category": "Développement",   "country": "US", "lang": "EN", "desc": "Éditeur de code front-end en ligne"},
    "deviantart.com":    {"category": "Art/Créatif",     "country": "US", "lang": "EN", "desc": "Communauté d'art en ligne"},
    "behance.net":       {"category": "Art/Créatif",     "country": "US", "lang": "Multi", "desc": "Portfolio créatif et design"},
    "dribbble.com":      {"category": "Art/Créatif",     "country": "US", "lang": "EN", "desc": "Portfolio design UI/UX"},
    "fiverr.com":        {"category": "Freelance",       "country": "IL", "lang": "EN", "desc": "Marketplace de services freelance"},
    "upwork.com":        {"category": "Freelance",       "country": "US", "lang": "EN", "desc": "Plateforme de travail freelance"},
    "etsy.com":          {"category": "E-commerce",      "country": "US", "lang": "Multi", "desc": "Marketplace d'articles artisanaux"},
    "ebay.com":          {"category": "E-commerce",      "country": "US", "lang": "Multi", "desc": "Marketplace d'achat/vente en ligne"},
    "about.me":          {"category": "Portfolio",       "country": "US", "lang": "Multi", "desc": "Page de profil personnel"},
    "gravatar.com":      {"category": "Identité",        "country": "US", "lang": "Multi", "desc": "Avatar universel lié à un email"},
    "keybase.io":        {"category": "Sécurité",        "country": "US", "lang": "EN", "desc": "Identité cryptographique vérifiée"},
    "producthunt.com":   {"category": "Tech",            "country": "US", "lang": "EN", "desc": "Découverte de nouveaux produits tech"},
    "soundcloud.com":    {"category": "Musique",         "country": "DE", "lang": "Multi", "desc": "Plateforme de partage musical"},
    "bandcamp.com":      {"category": "Musique",         "country": "US", "lang": "EN", "desc": "Plateforme musicale indépendante"},
    "vimeo.com":         {"category": "Vidéo",           "country": "US", "lang": "Multi", "desc": "Plateforme vidéo de qualité"},
    "dailymotion.com":   {"category": "Vidéo",           "country": "FR", "lang": "Multi", "desc": "Plateforme vidéo française"},
    "flickr.com":        {"category": "Photo",           "country": "US", "lang": "Multi", "desc": "Partage et stockage de photos"},
    "500px.com":         {"category": "Photo",           "country": "CA", "lang": "Multi", "desc": "Communauté de photographie"},
    "vsco.co":           {"category": "Photo",           "country": "US", "lang": "EN", "desc": "Édition et partage de photos"},
    "quora.com":         {"category": "Q&A",             "country": "US", "lang": "Multi", "desc": "Plateforme de questions-réponses"},
    "wordpress.com":     {"category": "Blog",            "country": "US", "lang": "Multi", "desc": "Plateforme de blogs"},
    "wattpad.com":       {"category": "Écriture",        "country": "CA", "lang": "Multi", "desc": "Plateforme d'histoires en ligne"},
    "tryhackme.com":     {"category": "Cybersécurité",   "country": "GB", "lang": "EN", "desc": "Apprentissage de la cybersécurité"},
    "hackthebox.com":    {"category": "Cybersécurité",   "country": "GR", "lang": "EN", "desc": "Challenges de hacking éthique"},
    "bugcrowd.com":      {"category": "Cybersécurité",   "country": "US", "lang": "EN", "desc": "Bug bounty et sécurité"},
    "hackerone.com":     {"category": "Cybersécurité",   "country": "US", "lang": "EN", "desc": "Plateforme de bug bounty"},
    "vk.com":            {"category": "Réseau social",   "country": "RU", "lang": "RU",  "desc": "Réseau social russe"},
    "ok.ru":             {"category": "Réseau social",   "country": "RU", "lang": "RU",  "desc": "Odnoklassniki, réseau social russe"},
    "weibo.com":         {"category": "Réseau social",   "country": "CN", "lang": "ZH",  "desc": "Réseau social chinois"},
    "xing.com":          {"category": "Professionnel",   "country": "DE", "lang": "DE",  "desc": "Réseau professionnel germanophone"},
}

def get_site_meta(url):
    for domain, meta in SITES_META.items():
        if domain in url:
            return meta
    return {"category": "Autre", "country": "??", "lang": "??", "desc": "Site non répertorié dans la base"}

def check_http_status(url):
    try:
        r = requests.head(url, timeout=8, allow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
        return r.status_code
    except:
        return None

def generate_text_report(username, results, duration):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(results)
    categories = {}
    countries = {}
    for r in results:
        categories[r["category"]] = categories.get(r["category"], 0) + 1
        countries[r["country"]] = countries.get(r["country"], 0) + 1

    cat_sorted = sorted(categories.items(), key=lambda x: -x[1])
    cty_sorted = sorted(countries.items(), key=lambda x: -x[1])

    lines = []
    lines.append("=" * 60)
    lines.append(f"  RAPPORT OSINT — USERNAME : @{username}")
    lines.append("=" * 60)
    lines.append(f"  Date       : {now}")
    lines.append(f"  Durée      : {duration}s")
    lines.append(f"  Profils    : {total} trouvé(s) sur 400+ sites")
    lines.append(f"  Source     : Sherlock Project")
    lines.append("=" * 60)
    lines.append("\n📊 RÉPARTITION PAR CATÉGORIE")
    lines.append("-" * 40)
    for cat, count in cat_sorted:
        lines.append(f"  {cat:<22} {count:>3}  {'█' * count}")
    lines.append("\n🌍 RÉPARTITION PAR PAYS")
    lines.append("-" * 40)
    for cty, count in cty_sorted:
        lines.append(f"  {cty:<10} {count:>3} profil(s)")
    lines.append("\n🔍 DÉTAIL DES PROFILS TROUVÉS")
    lines.append("-" * 40)
    for i, r in enumerate(results, 1):
        status_icon = "✅" if r["http_status"] == 200 else "⚠️" if r["http_status"] else "❓"
        lines.append(f"\n  [{i:>3}] {r['site']}")
        lines.append(f"        🔗 URL      : {r['url']}")
        lines.append(f"        📁 Catég.   : {r['category']}")
        lines.append(f"        🌍 Pays     : {r['country']} | Langue : {r['lang']}")
        lines.append(f"        📡 HTTP     : {status_icon} {r['http_status'] or 'N/A'}")
        lines.append(f"        ℹ️  Info     : {r['desc']}")
    lines.append("\n" + "=" * 60)
    lines.append(f"  FIN DU RAPPORT — @{username}")
    lines.append("=" * 60)
    return "\n".join(lines)


@app.route('/search')
def search():
    username = request.args.get('username', '').strip()
    check_status = request.args.get('check_status', 'false').lower() == 'true'

    if not username or len(username) > 50:
        return jsonify({'error': 'Username invalide'}), 400

    for c in [';', '&', '|', '`', '$', '>', '<', '"', "'"]:
        if c in username:
            return jsonify({'error': 'Caractères non autorisés'}), 400

    # Trouver le binaire sherlock dans le venv courant
    sherlock_bin = shutil.which('sherlock') or os.path.join(os.path.dirname(sys.executable), 'sherlock')

    try:
        start = datetime.utcnow()

        result = subprocess.run(
            [sherlock_bin, username, '--print-found', '--no-color', '--timeout', '10'],
            capture_output=True, text=True, timeout=120
        )

        duration = round((datetime.utcnow() - start).total_seconds(), 2)
        found = []

        for line in result.stdout.split('\n'):
            if '[+]' in line:
                url = line.replace('[+]', '').strip()
                match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                site = match.group(1) if match else url
                meta = get_site_meta(url)
                http_status = check_http_status(url) if check_status else None
                found.append({
                    "site":        site,
                    "url":         url,
                    "category":    meta["category"],
                    "country":     meta["country"],
                    "lang":        meta["lang"],
                    "desc":        meta["desc"],
                    "http_status": http_status
                })

        text_report = generate_text_report(username, found, duration)

        return jsonify({
            "username":    username,
            "total":       len(found),
            "duration_s":  duration,
            "scanned":     "400+",
            "timestamp":   datetime.utcnow().isoformat() + "Z",
            "results":     found,
            "text_report": text_report,
            "debug_sherlock_bin": sherlock_bin,
            "debug_stderr": result.stderr[:300]
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout — recherche trop longue'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    sherlock_bin = shutil.which('sherlock') or os.path.join(os.path.dirname(sys.executable), 'sherlock')
    return jsonify({
        'status': 'ok',
        'service': 'dosinit-sherlock-api',
        'sherlock_bin': sherlock_bin,
        'sherlock_exists': os.path.exists(sherlock_bin)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
