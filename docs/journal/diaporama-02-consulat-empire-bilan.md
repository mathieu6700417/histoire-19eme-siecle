# Bilan de production — diaporama 02 « Consulat et Empire »

Production du 2026-10-08, de 09:13 à 12:11 UTC (≈ 3 h, dont ≈ 25 min d'attente du rechargement
Gemini). Session principale `5d484a45-d04b-4dd0-839b-e338d90cb5fd`, trois sous-agents Opus
successifs : A (texte et images), B (voix, zone utile, caméra, musique, paroles),
C (surimpressions, vérification, build). Journal brut : `diaporama-02-consulat-empire.jsonl`
(77 entrées).

## Résultat

114 diapositives, 8 actes, 42,0 min ; 6 lectures, 3 épisodes, 4 intermèdes ; 65 lieux,
2 citations, 97 portraits, 2 objets, 1 manuscrit, 8 chiffres, 1 date républicaine, 1 mosaïque.
`verifier.py` : 0 erreur ; `npm run build` passe. Gemini : ≈ 2,7 $ (caméra 1,3 ; voix 1,0 ;
surimpressions 0,36). Décisions de l'utilisateur : « lieu de conservation non identifié »,
nouvel extrait de Bourgogne (le premier était refusé par le filtre de Gemini), extraits de
Georges Thill réutilisés.

## Où passent les tokens

| Agent | Durée | Requêtes | Cache écrit | Cache lu |
|---|---|---|---|---|
| A — texte et images | 55 min | 62 | 1,20 M | 12,3 M |
| B — voix, caméra, musique | 40 min | 124 | 0,48 M | 20,1 M |
| C — surimpressions, vérif | 75 min | 106 | 0,26 M | 18,6 M |
| Orchestration | — | 34 | 0,09 M | 3,0 M |
| **Total** | | **326** | **2,0 M** | **54,0 M** |

Pour comparaison, les chapitres écrivains 6 à 8 (3 agents en parallèle) : 3,7 M écrits,
120 M lus.

Constats :

1. **Le coût suit le nombre de tours, pas la taille des lectures.** Chaque requête relit tout
   le contexte en cache : B et C, avec 110 à 125 tours chacun, lisent 19 à 20 M tokens alors
   qu'ils n'écrivent presque rien. Les étapes les plus chères sont celles qui font beaucoup
   d'allers-retours : **portraits (C, 47 tours, 9 M)**, **caméra (B, 42 tours, 7,7 M)**,
   **zone utile (B, 53 tours, 7 M)**, **images (A, 7 M)**, **contrôle visuel (C, 4,4 M)**.
2. **Les images regardées sont la plus grosse dépense d'écriture en cache** (A-images-py
   0,64 M, B-camera 0,56 M) : chaque planche-contact lue s'ajoute au contexte pour le reste
   de l'agent. `tokens.py` ne compte pas les images dans le « poids traîné » (texte
   seulement) ; il les voit dans le cache écrit par phase.
3. **Les lectures de doc pèsent peu** : la spec 12 et le README, lus par morceaux ciblés,
   coûtent 0,3 à 0,7 M par agent. Le découpage en 3 agents est donc rentable : un agent
   unique aurait traîné les planches d'A pendant les 230 tours de B et C.
4. Les consignes d'économie ont été suivies (aucune lecture complète de `01-revolution.json`
   ni de `Diaporama.astro`) ; les plus gros résultats d'outil font 3 000 à 10 000 tokens.

## Temps et tours perdus (relevés dans le journal)

- A : un script maison écrasait ses propres résultats (2 min refaites) ; son générateur du
  JSON effaçait les champs d'`images.py` (un retéléchargement de 18 min évité de justesse).
- B : `voix.py` et `utile.py` lancés en parallèle → le premier a effacé les zones utiles du
  second (`commun.ecrire` réécrit tout le fichier depuis sa copie en mémoire).
- B : crédits Gemini épuisés en pleine étape (402) → écoute des chants impossible, attente.
- B : Gemini a « identifié » un 78 tours de travers (titre inventé) ; whisper local cassé.
- B : 6 propositions musicales de A introuvables en enregistrement libre.
- C : 11 erreurs de cadre de carte au premier `verifier.py` (fonds trop étroits).
- C : contrôle visuel, ~4 appels perdus sur l'horloge factice.

## Pistes, par gain estimé

| # | Piste | Gain attendu |
|---|---|---|
| 1 | **Outils « par lots »** : `images.py --lot` (recherche Commons + noms complets + planche-contact), `portraits.py --lot` (Wikidata, pré-remplissage du registre), `lieux.py --wikidata` (candidats + coordonnées + contrôle du fond de carte). | Les trois étapes les plus chères en tours (images, portraits, lieux) : ≈ 60 à 100 tours de moins, soit ≈ 15 M tokens lus. |
| 2 | **`commun.ecrire` fusionne au lieu d'écraser** (relit le fichier, ne remplace que ses champs, ou verrou). | Permet de lancer voix, zone utile, caméra et musique en parallèle : ≈ 20 min de moins, et plus de perte de champs. |
| 3 | **`captures.py`** (horloge factice, liste de diapositives, une planche). | Contrôle visuel en 1 à 2 tours au lieu de ~19. |
| 4 | **Registre partagé des enregistrements libres** (`registre-musique.json` : identifiant, année et preuve, licence, structure). | La recherche musicale ne repart pas de zéro à chaque période. |
| 5 | **Moins d'images regardées par le modèle** : planches plus denses, ne montrer que les cas signalés par les scripts (refus d'`utile.py`, caméras tenant > 7 s), recadrages de marge proposés automatiquement (`images.py --proposer-recadrage`, ~60 % des estampes). | Réduit le cache écrit d'A et B (≈ 1 M). |
| 6 | **`verifier.py --etape A|B|C`** (n'afficher que les contrôles de l'agent en cours) et **solde Gemini vérifié** avant chaque étape payante. | Sorties plus courtes ; pas de panne en cours de route. |
| 7 | **Fonds de carte élargis** (« monde » vers le sud pour Sainte-Hélène, « voisins » vers l'est) ; `CONSIGNES_VISIBLE` de `portraits.py` à généraliser (« la Révolution française » en dur). | Évite des erreurs qui reviendront aux périodes suivantes. |
| 8 | Caméra : ≈ 3 appels Gemini par image ; viser un seul appel, et ne refaire que les images dont la narration change. | ≈ 0,8 $ par période. |
| 9 | Orchestration : grouper les commandes `noter.py` avec la commande de travail coûte peu, mais la sortie de la commande suivante est alors comptée sous `noter.py` dans `tokens.py` ; écrire `noter.py` seul ou en fin de commande. | Mesure plus juste. |

## Chiffres bruts (`tokens.py`)

## Par fil (session principale et sous-agents)

| Fil | Requêtes | Entrée | Cache écrit | Cache lu | Sortie |
|---|---|---|---|---|---|
| principal | 34 | 76 | 86,213 | 2,962,974 | 26,708 |
| Diaporama Empire : surimpressions et vérif | 106 | 212 | 256,396 | 18,599,372 | 5,801 |
| Diaporama Empire : voix, caméra, musique | 124 | 248 | 477,887 | 20,078,812 | 4,798 |
| Diaporama Empire : écriture et images | 62 | 126 | 1,204,926 | 12,316,505 | 1,652 |
| **Total** | 326 | 662 | 2,025,422 | 53,957,663 | 38,959 |

## Par phase du journal

| Phase | Requêtes | Cache écrit | Cache lu | Sortie |
|---|---|---|---|---|
| C-portraits | 47 | 77,411 | 8,996,127 | 5,194 |
| B-camera | 42 | 562,444 | 7,663,596 | 1,422 |
| B-utile | 53 | 117,046 | 7,028,398 | 2,363 |
| A-images-py | 29 | 636,398 | 6,990,307 | 4,637 |
| C-controle-visuel | 19 | 20,828 | 4,415,664 | 1,761 |
| B-musique-traitement | 14 | 54,401 | 3,584,476 | 1,714 |
| A-plan | 18 | 122,112 | 2,759,396 | 717 |
| A-ecriture-json | 9 | 79,839 | 2,353,261 | 78 |
| B-verifier | 13 | 50,747 | 2,100,311 | 5,579 |
| C-lieux | 8 | 24,583 | 1,057,960 | 71 |
| C-build | 4 | 3,597 | 950,603 | 34 |
| C-bourgogne | 9 | 37,103 | 844,958 | 188 |
| (hors phase) | 13 | 94,603 | 775,721 | 12,521 |
| C-citations | 5 | 12,395 | 719,052 | 31 |
| C-verifier | 3 | 5,309 | 699,500 | 32 |
| C-surimpressions | 3 | 2,691 | 688,525 | 26 |
| B-voix | 10 | 7,352 | 683,301 | 753 |
| C-lecture | 11 | 41,400 | 670,854 | 136 |
| A-lecture | 10 | 55,552 | 653,217 | 884 |
| B-lecture | 6 | 19,611 | 322,436 | 818 |

## Par outil (résultats renvoyés au modèle)

| Outil | Appels | Tokens des résultats (est.) | Poids traîné (est.) |
|---|---|---|---|
| Bash sed | 24 | 50,806 | 3,615,500 |
| Bash python3 | 62 | 34,264 | 2,684,053 |
| Bash cat | 18 | 33,974 | 1,709,851 |
| Bash noter.py | 44 | 22,500 | 1,632,761 |
| Read | 38 | 10,543 | 938,390 |
| Bash ls | 7 | 8,372 | 683,724 |
| WebSearch | 7 | 6,047 | 360,862 |
| Bash portraits.py | 10 | 5,679 | 351,385 |
| Bash mkdir | 6 | 3,069 | 262,306 |
| Bash voix.py | 14 | 3,581 | 242,912 |
| Bash grep | 8 | 2,318 | 170,373 |
| Bash commun.py | 4 | 3,024 | 157,401 |
| Bash curl | 9 | 2,542 | 155,915 |
| Bash wikisource.py | 1 | 1,318 | 129,248 |
| Bash images.py | 6 | 2,363 | 105,594 |

## Les 15 résultats d'outil les plus lourds à traîner

| Poids traîné | Tokens | Fil | Outil | Appel |
|---|---|---|---|---|
| 938,390 | 10,543 | Diaporama Empire : surimpressions et vérif | Read | `/private/tmp/claude-501/-Users-mathieu-ai-projects-19eme-siecle/5d484a45-d04b-4dd0-839b-e3` |
| 628,220 | 6,220 | Diaporama Empire : surimpressions et vérif | Bash ls | `ls scripts/ecrivains/; grep -n -i 'extrait\\|id=\\|Russie\\|Moscou\\|Bérézina\\|retraite' src/c` |
| 435,499 | 4,785 | Diaporama Empire : surimpressions et vérif | Bash sed | `sed -n 672,880p scripts/diaporamas/README.md` |
| 406,110 | 3,301 | Diaporama Empire : voix, caméra, musique | Bash noter.py | `python3 scripts/journal/noter.py diaporama-02-consulat-empire debut B-lecture "Agent B dém` |
| 363,990 | 3,466 | Diaporama Empire : surimpressions et vérif | Bash noter.py | `python3 scripts/journal/noter.py diaporama-02-consulat-empire debut C-lecture "Agent C : l` |
| 356,644 | 3,876 | Diaporama Empire : surimpressions et vérif | Bash noter.py | `python3 scripts/journal/noter.py diaporama-02-consulat-empire fin C-bourgogne "Extrait acc` |
| 344,598 | 6,265 | Diaporama Empire : écriture et images | Bash sed | `sed -n 19,52p docs/specs/04-ecrivains-consulat-empire.md; grep -n -E '^#\|<Extrait\|auteur=\|` |
| 301,834 | 5,030 | Diaporama Empire : écriture et images | Bash sed | `sed -n 237,475p docs/specs/12-siecle-en-images.md` |
| 300,828 | 3,008 | Diaporama Empire : surimpressions et vérif | Bash sed | `sed -n 1084,1200p src/content/ecrivains/02-consulat-empire.mdx \| grep -v '^$' \| cut -c1-70` |
| 277,982 | 2,698 | Diaporama Empire : surimpressions et vérif | Bash sed | `sed -n 133,160p scripts/diaporamas/README.md; sed -n 398,497p scripts/diaporamas/README.md` |
| 271,627 | 2,244 | Diaporama Empire : voix, caméra, musique | Bash sed | `sed -n 173,252p scripts/diaporamas/README.md; sed -n 274,290p scripts/diaporamas/README.md` |
| 241,200 | 4,020 | Diaporama Empire : écriture et images | Bash sed | `sed -n 1,175p scripts/diaporamas/README.md; sed -n 253,274p scripts/diaporamas/README.md` |
| 240,933 | 2,170 | Diaporama Empire : voix, caméra, musique | Bash sed | `sed -n 291,397p scripts/diaporamas/README.md` |
| 231,796 | 2,126 | Diaporama Empire : voix, caméra, musique | Bash sed | `sed -n 266,300p docs/specs/12-siecle-en-images.md; sed -n 488,498p docs/specs/12-siecle-en` |
| 230,098 | 4,793 | Diaporama Empire : écriture et images | Bash cat | `cd /private/tmp/claude-501/-Users-mathieu-ai-projects-19eme-siecle/5d484a45-d04b-4dd0-839b` |

---

# Suite : retouches et outillage (2026-10-09)

Après la mise en ligne, l'utilisateur a regardé le diaporama et demandé une série de retouches,
traitées par 12 sous-agents Opus (journaux : `frise-simplifiee`, `camera-vivante`,
`cartes-animees`, `lectures-vers`, `decoupage-lecteur`, `outillage-python`, `generique`,
`enrichissements-02`, `tetes-coupees`, `portraits-objets`, `indicatif-original`, `orchestration`).
Livré en trois commits (126a578, ee4de03, a8405c6).

## Tokens de toute la session (`tokens.py 5d484a45-…`)

| | Requêtes | Cache écrit | Cache lu | Sortie |
|---|---|---|---|---|
| Production initiale (agents A, B, C) | 292 | 2,9 M | 51,0 M | 12 k |
| Retouches et outillage (12 agents) | 933 | 3,9 M | 140,8 M | 52 k |
| Orchestration (session principale) | 194 | 0,4 M | 39,5 M | 141 k |
| **Total** | **1 419** | **7,2 M** | **231 M** | **201 k** |

Gemini : ~2,7 $ (production) + ~6,3 $ (passe caméra sans plafond de réflexion) + ~0,9 $
(visages) + ~0,4 $ (enrichissement) + ~1 $ (Lyria) + ~0,2 $ (banc d'essai). Crédits épuisés
deux fois.

## Constats

1. **Les retouches ont coûté près de trois fois la production.** Ce que l'utilisateur a vu au
   visionnage (frise cassée, têtes coupées, épisodes pauvres, enrichissements absents, cadres
   faux) n'avait été repéré par aucun contrôle. Chaque défaut trouvé après coup a coûté un agent
   complet (8 à 30 M lus). → Contrôles automatiques ajoutés (`verifier.py` : dosage, épisodes,
   vignettes ; `camera.py --audit` : vues réelles, visages, portraits) ; `captures.py` pour un
   contrôle visuel en une commande.
2. **Le lecteur monolithique** (196 Ko) rendait chaque retouche chère et interdisait le
   parallélisme ; découpé en 27 modules (rendu identique au pixel). Les agents suivants ont
   travaillé à deux ou trois en parallèle sans conflit.
3. **Gemini sans plafond** : la réflexion libre faisait ~85 % du coût de la caméra. Banc d'essai :
   `gemini-3.8-flash` sans réflexion, ~0,006 $ par diapositive pour la caméra (dix fois moins).
   `--budget` dans chaque consigne d'agent.
4. **L'orchestration elle-même pèse** (39 M lus, 17 % du total) : une longue conversation qui relit
   tout son historique à chaque tour. → Une session par chantier, ou `/compact` entre deux.
5. **Reprendre un agent qui a déjà le contexte** (SendMessage) coûte bien moins qu'un nouvel agent
   pour une petite retouche (frise : 14 appels en 2 min ; indicatif : 12 appels).
6. Les agents ne peuvent ni écouter ni bien voir le mouvement : musique et caméra se jugent par
   l'utilisateur. Leur proposer tôt une page d'écoute ou un build local évite des allers-retours.

## Pour la période 03 (Restauration)

- Lire d'abord la spec 12, « Produire une période : leçons de Consulat et Empire ».
- Agent A prévoit enrichissements, épisodes riches, cartes et générique dès l'écriture ;
  `verifier.py` doit être sans avertissement de dosage avant toute voix.
- Outils par lots (`images.py --lot`, `portraits.py --lot`), `--budget` partout, `captures.py`.
- Montrer le build à l'utilisateur à mi-parcours (après les images et la caméra), pas seulement à la fin.
