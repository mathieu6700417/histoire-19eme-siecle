# Spec 18 — Un site pour plusieurs siècles

Décidée le 2026-10-14 avec l'utilisateur (questions une par une).

## But

Le site cesse d'être « Le XIXe siècle français » pour devenir **« Histoire de France »**,
capable d'accueillir **n'importe quel siècle** (ou période) par simple déclaration. Le XIXe
(1789-1900) en est le premier siècle, avec tout son contenu actuel. Aucun contenu n'est
préparé pour les autres siècles dans ce chantier.

## Décisions

1. **Périmètre** : tous les siècles, sans limite. Un siècle est une entrée de registre
   (`src/data/siecles.ts`) : identifiant (`xixe`), libellé (« xixᵉ siècle », chiffre romain
   en petites capitales), bornes (`1789`, `1900` : un siècle peut déborder ses bornes
   calendaires), chapeau d'une ou deux phrases, sections disponibles, ordre chronologique.
2. **Géographie** : France partout. Chaque siècle définit ses bornes ; la règle
   « France uniquement, sauf mention explicite dans une leçon » reste.
3. **Adresses** : préfixe par siècle pour toutes les pages.
   - `/` : sommaire des siècles ;
   - `/xixe/` : accueil du XIXe (l'actuelle page d'accueil, inchangée sur le fond) ;
   - `/xixe/lecons/<slug>/…`, `/xixe/ecrivains/…`, `/xixe/ecrivains/auteurs/`,
     `/xixe/diaporamas/…`.
   - Les **anciennes adresses redirigent en 301** vers les nouvelles (`/lecons/*`,
     `/ecrivains/*`, `/diaporamas/*` → `/xixe/…`) ; mécanisme : fichier `public/_redirects`
     (pris en charge par les assets statiques de Cloudflare Workers) — vérifier qu'il est
     bien honoré par `wrangler`, sinon solution équivalente.
   - Les anciennes adresses de **médias** (`/diaporamas/<slug>/…` en fichiers) n'ont pas à
     être redirigées, sauf si cela vient gratuitement avec la règle des pages.
4. **Accueil racine = sommaire des siècles** : liste sobre, un siècle par ligne, séparés par
   des filets fins : chiffre romain en petites capitales, bornes, chapeau, liens vers les
   sections disponibles (Leçons · Écrivains · Images). Seuls les siècles déclarés
   apparaissent (pas de siècles « à venir »). Titre de page « Histoire de France ».
5. **Nom du site** : « Histoire de France ». Dans un siècle, l'en-tête affiche aussi le
   siècle courant (« Histoire de France · xixᵉ siècle ») et la navigation de ce siècle
   (Accueil du siècle, Leçons, Écrivains, Images — seulement les sections qu'il possède) ;
   le nom du site ramène au sommaire. Titres d'onglets : `<page> · <siècle> · Histoire de France`
   (ou forme équivalente sobre). Pied de page généralisé.
6. **Sections facultatives par siècle** : les leçons existent toujours ; « Écrivains » et
   « Images » sont des modèles réutilisables qu'un siècle active quand il en a le contenu.
   Le code (composants, lecteur de diaporama, layouts) est partagé ; contenus, données et
   médias sont rangés par siècle.
7. **Dépôt, dossier local, Worker et domaine** : inchangés pour l'instant (renommage
   éventuel plus tard, à part).
8. **Rangement des fichiers par siècle** (par `git mv`, sans recopie) :
   - `src/content/lecons/xixe/<slug>.mdx` (+ sous-pages `xixe/<slug>/<sous>.mdx`) ;
     le siècle se déduit du premier segment de l'id ;
   - `src/content/ecrivains/xixe/NN-<slug>.mdx` ;
   - `src/data/diaporamas/xixe/…`, `public/xixe/diaporamas/<slug>/…` (et `commun`, `fonds`,
     `objets`, `portraits`, `manuscrits` sous `xixe/` aussi : rien n'est partagé entre
     siècles pour l'instant). Les médias sont sous `public/<siecle>/diaporamas/` et non
     `public/diaporamas/<siecle>/` : les redirections Cloudflare passent avant les fichiers
     statiques, la règle `/diaporamas/*` aurait donc capté les médias ; ainsi rangés, ils
     restent à côté de leur page (constat de l'implémentation, 2026-10-14) ;
   - données propres au XIXe (`auteurs.ts`, `artistes.ts`, `chapitres-ecrivains.ts`,
     `courants-politiques.ts`…) : sous `src/data/xixe/` si c'est simple, sinon laissées en
     place avec un commentaire — ne pas forcer un découpage qui casse plus qu'il n'apporte ;
   - `src/assets/oeuvres/` : idem, `xixe/` si les imports s'y prêtent ;
   - annotations (`docs/annotations/<slug>.jsonl`) et journaux : rangés sous `xixe/` si les
     scripts suivent, sinon laissés en place ;
   - caches (`.cache/diaporamas/…`) : ne pas déplacer, mais les scripts doivent continuer à
     les retrouver.
9. **Scripts de production** (`scripts/diaporamas`, `scripts/ecrivains`, `scripts/colab`,
   `scripts/journal`) : prennent le siècle en paramètre (`--siecle`, `xixe` par défaut) ;
   les chemins sont calculés en un seul endroit (`commun.py` pour les diaporamas). Le README
   des scripts et les specs de procédure (12, 00) sont mis à jour pour les nouveaux chemins.

## Invariants (rien ne doit changer pour le lecteur du XIXe)

- Toutes les pages actuelles existent à leur nouvelle adresse avec un rendu identique
  (hors en-tête et pied) ; les liens internes (y compris dans les MDX et les données)
  pointent vers les nouvelles adresses, aucun lien interne ne passe par une redirection.
- Les diaporamas jouent comme avant (images, clips, sons, musique, fonds, netteté).
- Design inchangé : monochrome, sobre (CLAUDE.md, section Design).
- `npm run build` passe ; `npm run verifier:ecrivains` passe ;
  `python3 scripts/diaporamas/verifier.py` passe sur chaque période ;
  `python3 scripts/diaporamas/annotations.py lister second-empire` retrouve les annotations ;
  `npm run annoter` fonctionne.

## Hors périmètre

Contenu d'un autre siècle, renommage du dépôt/Worker, frise globale des siècles,
mode sombre, commit et déploiement (sur demande de l'utilisateur seulement).
