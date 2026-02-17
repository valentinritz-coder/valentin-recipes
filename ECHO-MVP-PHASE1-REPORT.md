# Compte rendu demandé — `echo-mvp` (phase 1)

## Statut de l'analyse

Je n’ai pas trouvé de dépôt `echo-mvp` dans l’environnement fourni.

Vérifications effectuées :

- recherche d’un dossier `echo-mvp` dans `/workspace`
- recherche de fichiers clés attendus (`docker-compose.yml`, `README.md`, `services/api/app/main.py`, `apps/web/app.py`, etc.)

Résultat : aucun fichier/structure correspondant à `echo-mvp` n’est présent dans ce conteneur.

---

## 1) Arborescence (tree) et fichiers importants

Impossible à produire pour `echo-mvp` tant que le dépôt n’est pas disponible localement.

Quand le repo sera disponible, utiliser :

```bash
find . -maxdepth 3 -print
```

et lister ensuite les fichiers clés :

- `README.md`
- `docker-compose.yml`
- `.env.example`
- `services/api/app/main.py`
- `services/api/app/settings.py` (ou équivalent)
- `apps/web/app.py`
- `docs/product.md`
- `docs/privacy.md`

---

## 2) Résumé des fichiers clés

Non réalisable dans l’état actuel : les fichiers demandés ne sont pas présents dans le workspace.

---

## 3) Vérification `docker-compose up` (api + web + état API dans Streamlit)

Non réalisable dans l’état actuel, faute de dépôt `echo-mvp` et de `docker-compose.yml` associé.

Procédure à exécuter dès que le repo est fourni :

```bash
docker compose up --build
```

Puis vérifier :

- 2 services démarrés (`api`, `web`)
- l’UI Streamlit affiche l’état de l’API (health/status OK)

---

## 4) Commandes exactes (à utiliser dans `echo-mvp`)

### Lancer le projet

```bash
cp .env.example .env
docker compose up --build
```

### Arrêter

```bash
docker compose down
```

### Relance propre en supprimant les volumes (optionnel)

```bash
docker compose down -v
docker compose up --build
```

---

## 5) TODO phase 2 (API + SQLite + upload audio)

Checklist proposée :

- [ ] Ajouter une couche de persistance SQLite (fichier DB + migrations initiales).
- [ ] Définir un schéma de données pour les enregistrements audio et métadonnées.
- [ ] Créer les endpoints API CRUD de base (`POST/GET/DELETE`) pour les uploads.
- [ ] Implémenter l’upload audio côté API (validation type MIME + taille max).
- [ ] Stocker les fichiers audio (local volume en phase 2) avec nommage robuste.
- [ ] Ajouter endpoint de health enrichi (DB connectée, stockage accessible).
- [ ] Ajouter configuration via variables d’environnement (`DB_URL`, dossier upload, limites).
- [ ] Mettre à jour l’app Streamlit pour envoyer un fichier audio et afficher le résultat.
- [ ] Ajouter tests API (upload valide/invalide, erreurs, lecture métadonnées).
- [ ] Ajouter tests d’intégration Docker Compose (web ↔ api ↔ sqlite).
- [ ] Mettre à jour la doc produit (`docs/product.md`) et confidentialité (`docs/privacy.md`) pour l’audio.
- [ ] Ajouter règles de rétention/suppression des fichiers audio et logs associés.

---

Si vous fournissez le dépôt `echo-mvp` (ou son URL), je peux produire immédiatement la version complète attendue : arborescence réelle, résumé fichier par fichier, test `docker compose up`, corrections éventuelles, et validation finale.
