# Engrame : pilote Google Drive vers Frame.io

Objectif : réceptionner les exports des monteurs sur Drive, les classer dans Frame.io par client et projet, puis retirer les sources après confirmation du transfert. Le suivi des livrables, des responsables et des paiements va dans le dashboard Notion Engrame.

Le calcul doit tourner dans Codex Cloud toutes les six heures, PC éteint, sans Make ni serveur externe. Cette possibilité reste à vérifier dans le compte avant de lancer une synchronisation.

## État du pilote

`preflight.py` est un diagnostic en lecture seule. Il vérifie les dossiers Drive/Frame.io, les permissions d'un échantillon et le disque disponible. Il ne transfère ni ne supprime de fichiers. La synchronisation complète n'est pas encore implémentée.

## Lancer les tests

Python 3.10 ou supérieur, sans dépendance externe :

```sh
python -m unittest -v test_preflight
```

Pour le diagnostic réel, copier `config.example.json` en `config.json`, renseigner les identifiants des dossiers, puis configurer les deux clés d'accès dans le coffre-fort du nouvel environnement Codex Cloud :

- `ENGRAME_DRIVE_ACCESS_TOKEN`, pour `www.googleapis.com` ;
- `ENGRAME_FRAME_ACCESS_TOKEN`, pour `api.frame.io`.

```sh
python preflight.py --config config.json --offline
python preflight.py --config config.json
```

Les jetons servent à l'essai ; leur renouvellement doit être testé avant toute exploitation automatique. Ne pas ajouter de jetons, de configuration réelle ou de vidéos à ce dépôt.

Voir `PREPARATION-CLOUD.md` pour les vérifications restantes et les sources techniques.
