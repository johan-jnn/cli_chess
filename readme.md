# ♟️ Terminal Chess Game

Un jeu d'échecs complet jouable **dans le terminal**, écrit en **Python**, avec gestion des règles officielles et affichage dynamique du plateau.  
Ce projet est pensé pour les passionnés de stratégie et les développeurs souhaitant explorer la logique des échecs.

---

## 🔧 Fonctionnalités principales

- ✅ Interface en ligne de commande (CLI)
- ✅ Mode **tour par tour**, avec **plateau qui se retourne** à chaque coup
- ✅ Vérification des **coups légaux** (mouvements, prises, promotions...)
- ✅ Détection de l’**échec** et du **mat**
- ✅ Prise en charge du petit/grand rock
- ✅ Prise en charge de la **notation algébrique** pour l'encodage et le décodage des coups ([Algebraic notation](<https://en.wikipedia.org/wiki/Algebraic_notation_(chess)>))
- ✅ **Annulation de coup** (commande `:cancel`)
- ✅ Commandes spéciales pour améliorer l’expérience utilisateur

---

## 🚧 Fonctionnalités à venir

- ⏳ Vérification des **situations de pat** :
  - [x] Roi seul et bloqué
  - [x] Manque de materiel
  - [ ] Répétition de coups (3x)
  - [ ] Proposition de pat
- ⏳ **Jeu contre un bot** (structure déjà en place, IA à implémenter)
- ⏳ Possibilité de jouer en mode [**Chess920**](https://fr.wikipedia.org/wiki/%C3%89checs_al%C3%A9atoires_Fischer)

---

## 💬 Commandes accessibles en jeu

| Commande         | Description                                     |
| ---------------- | ----------------------------------------------- |
| `:exit`          | Ferme immédiatement le jeu                      |
| `:cancel`        | Annule le dernier coup joué                     |
| `:undo`          | Alias de la commande `:cancel`                  |
| `:pause`         | Met en pause la partie (jusqu'à reprise)        |
| `:clear`         | Effacer le contenu de l'écran                   |
| `:legals <case>` | Affiche les coups légaux depuis une case donnée |

> Exemple : `:legals e2` affichera tous les coups possibles depuis la case **e2**

---

## ▶️ Démarrer le jeu

Assure-toi d’avoir Python 3.8+ installé.

```bash
git clone https://github.com/johan-jnn/cli_chess.git
cd cli_chess
python __main__.py [--test | --units]
```

### 🐋 Utiliser avec Docker

```bash
# En téléchargeant le repo :
git clone https://github.com/johan-jnn/cli_chess.git
cd cli_chess
docker run --rm -it $(docker build -q .) [--test | --units]

# Sans télécharger le repo :
docker run --rm -it $(docker build -q 'https://github.com/johan-jnn/cli_chess.git') [--test | --units]
```

---

## 🧩 Idées futures

- Mode 2 joueurs en réseau
- Sauvegarde et reprise de partie
- Analyse de parties jouées
