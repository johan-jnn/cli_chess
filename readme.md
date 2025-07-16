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
  - Roi seul et bloqué
  - Répétition de coups (3x)
  - Proposition de pat
- ⏳ **Jeu contre un bot** (structure déjà en place, IA à implémenter)

---

## 💬 Commandes accessibles en jeu

| Commande         | Description                                     |
| ---------------- | ----------------------------------------------- |
| `:exit`          | Ferme immédiatement le jeu                      |
| `:cancel`        | Annule le dernier coup joué                     |
| `:pause`         | Met en pause la partie (jusqu'à reprise)        |
| `:legals <case>` | Affiche les coups légaux depuis une case donnée |

> Exemple : `:legals e2` affichera tous les coups possibles depuis la case **e2**

---

## ▶️ Démarrer le jeu

Assure-toi d’avoir Python 3.8+ installé.

```bash
git clone https://github.com/johan-jnn/terminal-chess.git
cd terminal-chess
python __main__.py
```

---

## 🧩 Idées futures

- Mode 2 joueurs en réseau
- Sauvegarde et reprise de partie
- Analyse de parties jouées
