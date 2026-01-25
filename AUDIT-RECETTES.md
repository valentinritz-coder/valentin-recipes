# Audit automatique du dépôt Valentin Recipes

> **Portée** : audit éditorial et structurel du dépôt (scan complet, hors `.git`).

---

## 0) Scan initial

### Structure repérée
- Racine : `README.md` + dossier `recettes/` + (dossier `images/` **décrit** dans le README mais **absent**).
- Un **template de recette** est présent : `recettes/_template-recette.md`.

### Comptages (scan complet)
- **Total fichiers (hors .git)** : 21
- **Recettes (.md)** : 17
- **Recettes sans extension .md** : 1 (`recettes/drinks/iced-tea`)
- **Images présentes** : 0
- **Liens d’images dans les recettes** : 14
- **Recettes sans image** : 4
- **Recettes sans “Personnes”** : 4
- **Recettes sans “Conseils / astuces”** : 2
- **Recettes sans “Suggestions de service”** : 3

### Méthode & commandes utilisées
- `find . -type f ! -path './.git/*' | wc -l`
- `find recettes -type f -name "*.md" | wc -l`
- `find . -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" \) | wc -l`
- Script Python local (regex Markdown) pour détecter sections + métadonnées.

---

## 1) Inventaire & structure

### Organisation par dossiers
- `recettes/plats-principaux/` (7 recettes)
- `recettes/accompagnements/` (4 recettes)
- `recettes/desserts/` (3 recettes)
- `recettes/sauces/` (3 recettes)
- `recettes/drinks/` (1 recette **sans extension .md**)

### Conventions observées
- **Template standard** clair (H1 + image + métadonnées + sections). 
- **Variantes de métadonnées** : `Personnes` vs `Quantité` vs `Rendement`.

---

## 2) Qualité Markdown & cohérence éditoriale

### Format standard attendu (d’après le template)
- Titre H1
- Image (lien relatif)
- Personnes, Préparation, Cuisson, Matériel
- Sections : Ingrédients, Préparation, Conseils / astuces, Suggestions de service

### Écarts & incohérences
- **Images manquantes** : 4 recettes sans image.
- **Placeholder d’image** : un chemin `CHEMIN/VERS-IMAGE.jpg` reste dans une recette.
- **Métadonnées non uniformes** : `Rendement`, `Quantité` au lieu de `Personnes`.
- **Sections manquantes** : certaines recettes n’ont pas `Conseils / astuces` ou `Suggestions de service`.

---

## 3) Utilisabilité cuisine (terrain)

### Points forts
- Étapes claires, précisions sur la texture et la température (ex. cuisson lente, cocotte, temps de repos).
- Style simple et convivial, fidèle à la cuisine “maison”.

### Ambiguïtés fréquentes
- **Portions** non indiquées pour certaines sauces/accompagnements.
- Ingrédients spécifiques parfois **sans substitution** (ex. variétés de thé, charcuteries).

---

## 4) Couverture & lacunes (par rapport au style)

### Couverture
- **Mijotés/cocotte** bien représentés (chili, pulled pork, poulet cocotte).
- **Accompagnements rustiques** présents (purée, cornbread, pickles).
- **Sauces maison** solides (barbecue, ketchup, gravy).

### Lacunes
- Peu de **légumes simples** (haricots, maïs, carottes rôties, etc.).
- Peu de **plats poêle/grill** rapides.
- **Index** de navigation absent (par type, temps, ingrédient).

---

## 5) Recommandations actionnables (Top 10)

| # | Action | Impact | Effort |
|---|---|---|---|
| 1 | Ajouter le dossier `images/` + assets réels (ou retirer liens d’images cassés). | Élevé | Moyen |
| 2 | Remplacer les placeholders d’images. | Élevé | Faible |
| 3 | Uniformiser les métadonnées (`Personnes`, `Préparation`, `Cuisson`, `Matériel`). | Élevé | Faible |
| 4 | Renommer `recettes/drinks/iced-tea` en `.md`. | Élevé | Faible |
| 5 | Ajouter “Suggestions de service” aux recettes qui manquent. | Moyen | Faible |
| 6 | Ajouter substitutions pour ingrédients spécifiques. | Moyen | Faible |
| 7 | Créer un index (README ou `index.md`) par type/temps. | Élevé | Moyen |
| 8 | Standardiser unités (c. à soupe / c. à café). | Moyen | Faible |
| 9 | Créer une checklist PR “nouvelle recette”. | Moyen | Faible |
| 10 | Ajouter un lint Markdown + check d’images en CI. | Moyen | Moyen |

---

## 6) Livrables

### A) Rapport synthèse (max 1 page)

Le dépôt est clair, convivial et cohérent avec une **cuisine familiale généreuse**. Le **template** est un atout majeur, mais l’application est inégale : métadonnées non uniformes, sections parfois absentes, et un fichier boisson sans extension `.md` qui risque d’être oublié par les outils. Le **point critique** est l’absence d’images dans le dépôt alors que de nombreux liens d’illustrations existent. Priorités : **réparer la chaîne d’images**, **uniformiser les métadonnées**, et **compléter Conseils/Suggestions** sur les recettes incomplètes. Un **index de navigation** améliorerait fortement l’usage quotidien.

### B) Tableau des problèmes récurrents

| Problème | Fréquence (estimation) | Exemple (fichier + extrait) | Fix recommandé |
|---|---|---|---|
| Liens d’images cassés (dossier manquant) | Très fréquent | `![Sauce barbecue maison](../../images/sauces/sauce-barbecue-originale-hero.jpg)` | Ajouter `images/` ou retirer liens temporaires. |
| Placeholder d’image | Ponctuel | `![Photo du plat](../../images/CHEMIN/VERS-IMAGE.jpg)` | Remplacer par une vraie image. |
| Métadonnées non standardisées | Fréquent | `**Rendement** : ~500 ml` | Harmoniser avec `Personnes`. |
| Sections manquantes | Moyen | Recette sans `## Suggestions de service` | Ajouter 2–3 suggestions. |
| Recette sans extension `.md` | Ponctuel | `recettes/drinks/iced-tea` | Renommer en `.md`. |

### C) Checklist “nouvelle recette” (10–15 points)

1. Titre H1 clair
2. Image valide (ou TODO explicite)
3. Personnes indiquées
4. Préparation (temps)
5. Cuisson (temps)
6. Matériel principal
7. Ingrédients listés avec unités
8. Ingrédients groupés si besoin
9. Préparation en étapes numérotées
10. Températures/durées explicites
11. Conseils / astuces
12. Suggestions de service
13. Substitutions pour ingrédients rares
14. Lien image vérifié
15. Conformité au template

### D) Mini style guide (10 règles max)

1. Utiliser le template comme base
2. Toujours inclure Personnes, Préparation, Cuisson, Matériel
3. Unités cohérentes (c. à soupe / c. à café)
4. Ingrédients groupés par section
5. Étapes numérotées avec verbe d’action
6. Températures en °C, temps en min/h
7. Conseils pratiques systématiques
8. Suggestions de service systématiques
9. Substitutions pour ingrédients spécifiques
10. Pas de placeholder d’image

