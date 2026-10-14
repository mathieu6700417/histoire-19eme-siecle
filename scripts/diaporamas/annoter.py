#!/usr/bin/env python3
"""Serveur local des annotations de visionnage (spec 15) : `npm run annoter`.

    python3 scripts/diaporamas/annoter.py [--port 4330] [--sans-build] [--sans-capture]

1. Construit le site en mode annotation (`ANNOTATIONS=1 astro build --outDir
   dist-annotations`) : seul ce build embarque l'outil (src/scripts/diaporama/annotations.ts).
   `dist/` n'est ni lu ni modifié.
2. Sert `dist-annotations/` sur 127.0.0.1 (port libre, affiché), requêtes Range comprises (audio).
3. Point d'écriture, limité à `docs/annotations/<siecle>/` (bibliothèque : annotations.py) :
     GET    /__annotations/<slug>          liste
     POST   /__annotations/<slug>          création (JSON)
     PUT    /__annotations/<slug>/<id>     texte, catégorie
     DELETE /__annotations/<slug>/<id>     suppression (et sa capture)
     GET    /__annotations/<slug>/<id>.jpg capture
4. Capture : après chaque création, en tâche de fond, le lecteur est rejoué sans tête au même
   instant (`captures.py`, horloge factice, fenêtre de l'utilisateur) ; le JPEG (1 280 px au plus)
   est écrit dans `docs/annotations/<siecle>/<slug>/<id>.jpg` et le champ `capture` complété. En cas
   d'échec (Playwright absent…), `capture` reste `null`. Au lancement, les captures manquantes
   sont retentées une fois.
"""
from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import annotations as ann  # noqa: E402

RACINE = ann.RACINE
DIST = RACINE / 'dist-annotations'
PREFIXE = '/__annotations/'
LARGEUR_CAPTURE = 1280
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('text/javascript', '.js')


def journal(*a) -> None:
    print(*a, flush=True)


# --- Captures en tâche de fond ---------------------------------------------------------------------

class Captures(threading.Thread):
    """File de captures : un seul Chromium sans tête, lancé à la première demande et gardé."""

    def __init__(self, port: int, actif: bool):
        super().__init__(daemon=True)
        self.port, self.actif, self.file = port, actif, queue.Queue()
        self.nav = self.pw = None

    def demander(self, a: dict) -> None:
        if self.actif:
            self.file.put(a)

    @staticmethod
    def instant(a: dict) -> str | None:
        """Instant au format de captures.py (`n:t`, `n:sT`, `n:cT`, `o:T`, `f:T`)."""
        l = a['lieu']
        t = f"{max(0.0, l.get('instant') or 0):.2f}"
        if l['type'] == 'generique':
            return f'o:{t}'
        if l['type'] == 'recapitulatif':
            return f'f:{t}'
        if l.get('n') is None:
            return None
        genre = {'carton': 'c', 'chant': 's', 'galerie': 's', 'lecture': 's', 'episode': 's'}.get(l['type'], '')
        return f"{l['n']}:{genre}{t}"

    def capturer(self, a: dict) -> str | None:
        import captures
        from PIL import Image
        item = self.instant(a)
        if not item:
            return None
        if not self.nav:
            from playwright.sync_api import sync_playwright
            self.pw = sync_playwright().start()
            self.nav = self.pw.chromium.launch(executable_path=captures.chromium(), args=['--autoplay-policy=no-user-gesture-required'])
        slug, ident, ecran = a['slug'], a['id'], a['ecran']
        l, h = ecran.get('fenetre') or (1280, 760)
        taille = (max(640, min(2560, int(l))), max(400, min(1600, int(h))))
        # Sans l'outil d'annotation dans la page ; sous-titres comme chez l'utilisateur.
        init = "window.__sansAnnotations = true; try { localStorage.setItem('diaporamas-sous-titres', '%s'); } catch {}" % ('oui' if ecran.get('sous_titre') is not None or a['lieu']['type'] not in ('diapositive', 'plan') else 'non')
        # Première diapositive d'un acte : l'ouverture en volets suit le temps réel (README, « Captures »).
        attente = 9000 if self.ouvre_acte(slug, a['lieu']) else 2500
        dossier = ann.fichier(slug).with_suffix('')
        dossier.mkdir(parents=True, exist_ok=True)
        png = dossier / f'.{ident}.png'
        try:
            erreurs = captures.capturer(self.nav, f'http://127.0.0.1:{self.port}{ann.c.url_diaporama(slug, ann.c.siecle_du_slug(slug))}', 'ordinateur', item, attente, png, taille=taille, init=init)
            for e in erreurs:
                journal(f'  capture {ident} : erreur de page : {e}')
            im = Image.open(png).convert('RGB')
            if im.width > LARGEUR_CAPTURE:
                im = im.resize((LARGEUR_CAPTURE, round(im.height * LARGEUR_CAPTURE / im.width)), Image.LANCZOS)
            im.save(dossier / f'{ident}.jpg', quality=85, optimize=True)
        finally:
            png.unlink(missing_ok=True)
        return f'{slug}/{ident}.jpg'

    @staticmethod
    def ouvre_acte(slug: str, lieu: dict) -> bool:
        d = ann._periode(slug)
        return bool(d) and lieu['type'] in ('diapositive', 'plan') and any(x.get('debut') == lieu.get('n') for x in d.get('actes', []))

    def run(self) -> None:
        while True:
            a = self.file.get()
            try:
                chemin = self.capturer(a)
            except Exception as e:  # Playwright absent, Chromium introuvable, page en erreur…
                journal(f"  capture {a['id']} impossible ({type(e).__name__} : {e}) : capture = null")
                try:
                    if self.nav:
                        self.nav.close()
                except Exception:
                    pass
                self.nav = None
                continue
            if chemin and not ann.poser_capture(a['slug'], a['id'], chemin):
                (ann.dossier(a['slug']) / chemin).unlink(missing_ok=True)   # annotation supprimée entre-temps
            elif chemin:
                journal(f'  capture {chemin}')


# --- Serveur ----------------------------------------------------------------------------------------

class Requete(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'annoter'
    captures: Captures

    def log_message(self, *a):
        pass

    # Fichiers statiques (dist-annotations), avec requêtes Range.
    def statique(self, corps: bool) -> None:
        chemin = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        f = (DIST / chemin.lstrip('/')).resolve()
        if DIST.resolve() not in (f, *f.parents):
            return self.erreur(403, 'hors du site')
        if f.is_dir():
            if not chemin.endswith('/'):
                self.send_response(301)
                self.send_header('Location', chemin + '/')
                self.send_header('Content-Length', '0')
                return self.end_headers()
            f = f / 'index.html'
        code = 200
        if not f.is_file():
            f, code = DIST / '404.html', 404
            if not f.is_file():
                return self.erreur(404, 'introuvable')
        taille = f.stat().st_size
        debut, fin = 0, taille - 1
        m = re.fullmatch(r'bytes=(\d*)-(\d*)', self.headers.get('Range', '').strip())
        if m and code == 200 and (m.group(1) or m.group(2)):
            if m.group(1):
                debut = int(m.group(1))
                fin = min(int(m.group(2)), taille - 1) if m.group(2) else taille - 1
            else:
                debut = max(0, taille - int(m.group(2)))
            if debut > fin or debut >= taille:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{taille}')
                self.send_header('Content-Length', '0')
                return self.end_headers()
            code = 206
        self.send_response(code)
        type_ = mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
        self.send_header('Content-Type', type_ + ('; charset=utf-8' if type_.startswith('text/') or type_.endswith('json') else ''))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Length', str(fin - debut + 1))
        if code == 206:
            self.send_header('Content-Range', f'bytes {debut}-{fin}/{taille}')
        self.end_headers()
        if not corps:
            return
        with f.open('rb') as h:
            h.seek(debut)
            reste = fin - debut + 1
            while reste > 0:
                bloc = h.read(min(1 << 16, reste))
                if not bloc:
                    break
                self.wfile.write(bloc)
                reste -= len(bloc)

    def json(self, code: int, objet) -> None:
        corps = json.dumps(objet, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def erreur(self, code: int, message: str) -> None:
        self.json(code, {'erreur': message})

    def local(self) -> bool:
        """Même origine seulement : hôte local, et pas d'origine étrangère pour les écritures."""
        hote = self.headers.get('Host', '')
        port = self.server.server_address[1]
        if hote not in (f'127.0.0.1:{port}', f'localhost:{port}'):
            return False
        origine = self.headers.get('Origin')
        return origine is None or origine in (f'http://127.0.0.1:{port}', f'http://localhost:{port}')

    def api(self, methode: str) -> None:
        if not self.local():
            return self.erreur(403, 'origine refusée')
        parties = [urllib.parse.unquote(p) for p in urllib.parse.urlsplit(self.path).path[len(PREFIXE):].split('/') if p]
        try:
            if not parties or len(parties) > 2:
                return self.erreur(404, 'chemin inconnu')
            slug = parties[0]
            ann.fichier(slug)   # valide le slug
            if len(parties) == 1 and methode == 'GET':
                return self.json(200, {'annotations': ann.lire(slug)})
            if len(parties) == 2 and methode == 'GET' and parties[1].endswith('.jpg') and ann.ID.fullmatch(parties[1][:-4]):
                f = ann.dossier(slug) / slug / parties[1]
                if not f.is_file():
                    return self.erreur(404, 'pas de capture')
                corps = f.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(corps)))
                self.end_headers()
                return self.wfile.write(corps)
            if methode in ('POST', 'PUT'):
                if 'application/json' not in self.headers.get('Content-Type', ''):
                    return self.erreur(415, 'JSON attendu')
                n = int(self.headers.get('Content-Length') or 0)
                if n > 200_000:
                    return self.erreur(413, 'trop long')
                donnees = json.loads(self.rfile.read(n) or b'{}')
                if not isinstance(donnees, dict):
                    return self.erreur(400, 'objet attendu')
            if len(parties) == 1 and methode == 'POST':
                a, nouvelle = ann.creer(slug, donnees)
                if nouvelle:
                    journal(f"+ {slug} {a['id']} [{a['categorie']}] {ann.lieu_lisible(a)} : {a['texte'][:60]}")
                    self.captures.demander(a)
                return self.json(201 if nouvelle else 200, {'annotation': a, 'annotations': ann.lire(slug)})
            if len(parties) == 2 and ann.ID.fullmatch(parties[1]):
                if methode == 'PUT':
                    a = ann.modifier(slug, parties[1], donnees)
                    journal(f"~ {slug} {a['id']} modifiée")
                    return self.json(200, {'annotation': a, 'annotations': ann.lire(slug)})
                if methode == 'DELETE':
                    ann.supprimer(slug, parties[1])
                    journal(f'- {slug} {parties[1]} supprimée')
                    return self.json(200, {'annotations': ann.lire(slug)})
            return self.erreur(405, 'méthode ou chemin refusé')
        except ann.Refus as e:
            return self.erreur(400, str(e))
        except KeyError:
            return self.erreur(404, 'annotation introuvable')
        except (ValueError, OSError) as e:
            return self.erreur(500 if isinstance(e, OSError) else 400, str(e))

    def do_GET(self):
        self.api('GET') if self.path.startswith(PREFIXE) else self.statique(True)

    def do_HEAD(self):
        self.statique(False)

    def do_POST(self):
        self.api('POST') if self.path.startswith(PREFIXE) else self.erreur(405, 'lecture seule')

    def do_PUT(self):
        self.api('PUT') if self.path.startswith(PREFIXE) else self.erreur(405, 'lecture seule')

    def do_DELETE(self):
        self.api('DELETE') if self.path.startswith(PREFIXE) else self.erreur(405, 'lecture seule')


class Serveur(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, *a):   # connexions coupées par le navigateur (médias abandonnés)
        pass


def construire() -> None:
    journal('Construction du site en mode annotation (dist-annotations/)…')
    env = {**os.environ, 'ANNOTATIONS': '1'}
    npx = shutil.which('npx') or 'npx'
    r = subprocess.run([npx, 'astro', 'build', '--outDir', str(DIST)], cwd=RACINE, env=env, capture_output=True, text=True)
    if r.returncode:
        sys.exit((r.stdout + r.stderr)[-3000:] + '\nÉchec de la construction.')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--port', type=int, default=0, help='port (par défaut : un port libre)')
    ap.add_argument('--sans-build', action='store_true', help='sert dist-annotations/ tel quel')
    ap.add_argument('--sans-capture', action='store_true', help='pas de capture d\'écran (capture : null)')
    a = ap.parse_args()
    if not a.sans_build:
        construire()
    if not (DIST / 'index.html').exists():
        sys.exit('dist-annotations/ absent : relancer sans --sans-build')
    ann.DOSSIER.mkdir(parents=True, exist_ok=True)
    srv = Serveur(('127.0.0.1', a.port), Requete)
    port = srv.server_address[1]
    Requete.captures = Captures(port, not a.sans_capture)
    Requete.captures.start()
    for slug in ann.slugs():   # captures manquantes (serveur arrêté pendant une prise) : une nouvelle tentative
        for x in ann.lire(slug):
            if not x.get('capture'):
                Requete.captures.demander(x)
    journal(f'Annotations de visionnage : http://127.0.0.1:{port}{ann.c.url_section()}')
    for f in sorted(DIST.glob('*/diaporamas/*/index.html')):   # toutes les périodes, tous siècles
        journal(f'  http://127.0.0.1:{port}/{f.relative_to(DIST).parent}/')
    journal('A : annoter · L : liste · Ctrl+C : arrêter. Écritures dans docs/annotations/<siecle>/.')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        journal('\nArrêt.')


if __name__ == '__main__':
    main()
