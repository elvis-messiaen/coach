# Coach App

Une application de coaching moderne développée avec Django et Tailwind CSS, permettant la gestion de rendez-vous, la différenciation des rôles (coach/client), et une expérience utilisateur minimaliste et responsive.

---

## Sommaire
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
  - [1. Cloner le dépôt](#1-cloner-le-dépôt)
  - [2. Créer et activer un environnement virtuel Python](#2-créer-et-activer-un-environnement-virtuel-python)
  - [3. Installer les dépendances Python](#3-installer-les-dépendances-python)
  - [4. Installer les dépendances Node.js (pour Tailwind)](#4-installer-les-dépendances-nodejs-pour-tailwind)
  - [5. Configurer la base de données](#5-configurer-la-base-de-données)
  - [6. Compiler Tailwind CSS](#6-compiler-tailwind-css)
- [Lancement du projet](#lancement-du-projet)
- [Utilisation](#utilisation)
  - [Accès client](#accès-client)
  - [Accès coach](#accès-coach)
- [Gestion des utilisateurs et rôles](#gestion-des-utilisateurs-et-rôles)
- [Dépannage](#dépannage)
- [Structure du projet](#structure-du-projet)

---

## Fonctionnalités
- Prise de rendez-vous avec sélection d'exercice, date et créneau horaire
- Interface différenciée pour coach et client
- Gestion des notes et historique pour le coach
- Design minimaliste, moderne, responsive (100% Tailwind )
- Authentification, inscription, gestion du mot de passe

---

## Prérequis
- **Python** ≥ 3.10
- **pip** (installé avec Python)
- **Node.js** ≥ 18.x et **npm** ≥ 9.x (pour Tailwind CSS)
- **Git** (pour cloner le dépôt)

> Compatible Windows, macOS, Linux

---

## Installation

### 1. Cloner le dépôt
```sh
git clone https://github.com/elvis-messiaen/coach.git
cd coach
```

### 2. Créer et activer un environnement virtuel Python
**Windows** :
```sh
python -m venv .venv
.venv\Scripts\activate
```
**macOS/Linux** :
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances Python
```sh
pip install -r coach/requirements.txt
```

### 4. Installer les dépendances Node.js (pour Tailwind)
```sh
cd coach/coach/theme/static_src
npm install
```

### 5. Configurer la base de données
```sh
cd ../../../..
python manage.py migrate
```

### 6. Compiler Tailwind CSS
**À chaque modification des templates ou du CSS, recompiler Tailwind :**
```sh
cd coach
python manage.py tailwind build
```

---

## Lancement du projet

1. **Démarrer le serveur Django**
   ```sh
   python manage.py runserver
   ```
2. Accéder à l'application sur http://127.0.0.1:8000/accounts/register/

---

## Utilisation

### Accès client
- Inscrivez-vous via la page d'inscription.
- Prenez rendez-vous en choisissant un exercice, une date, et un créneau horaire.
- Consultez vos rendez-vous et leur historique.

### Accès coach
- Un utilisateur coach doit être créé par un administrateur ou promu via l'interface d'admin Django.
- Accédez au dashboard coach pour voir, valider, refuser ou annoter les rendez-vous.
- Consultez l'historique des clients et ajoutez des notes de suivi.

---

## Gestion des utilisateurs et rôles
- **Client** : rôle par défaut à l'inscription.
- **Coach** : rôle attribué via l'admin Django (`is_coach` sur le profil utilisateur).
- Accès coach protégé par authentification et vérification du rôle.

---

## Dépannage
- **Problème de CSS ou de design** :
  - Recompiler Tailwind (`python manage.py tailwind build`)
  - Vider le cache navigateur
- **Erreur de migration** :
  - Vérifier la version de Python et relancer `python manage.py migrate`
- **Problème d'installation de dépendances** :
  - Vérifier que l'environnement virtuel est activé
  - Vérifier que Node.js et npm sont installés (`node -v`, `npm -v`)

---

## Structure du projet

```
coach/
  coach/                # Racine Django
    accounts/           # Authentification et gestion utilisateurs
    coach/              # Config Django
    coach_app/          # App principale (rendez-vous, dashboard, etc.)
      templates/
        coach_app/      # Templates principaux
    theme/              # App Tailwind (CSS)
      static_src/       # Source Tailwind (styles.css, package.json)
      static/css/dist/  # CSS généré par Tailwind
  manage.py             # Entrypoint Django
  requirements.txt      # Dépendances Python
```

---

## Bonnes pratiques
- Toujours activer l'environnement virtuel avant toute commande Python
- Toujours recompiler Tailwind après modification des templates ou du CSS
- Ne jamais modifier directement le CSS généré (`dist/styles.css`)
- Utiliser l'interface d'admin Django pour la gestion avancée des utilisateurs

