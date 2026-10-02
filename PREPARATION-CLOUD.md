# Engrame — pilote Drive → Frame.io dans Codex Cloud

État au 2 octobre 2026 : pilote préparé localement ; accès GitHub vérifié dans le chat cloud « Set up Mwac » ; aucune synchronisation active.
Responsable : Codex. Objectif demandé : exécution dans le cloud OpenAI toutes les six heures, PC éteint, sans Make ni hébergement de calcul externe.

## Configuration envisagée

- Environnement privé `engrame-drive-frame-sync` dans Codex Cloud.
- Dépôt de code dédié, sans vidéos, secrets ni données des clients.
- Google Drive reste le point de dépôt ; Frame.io reste la destination.
- Traitement des exports un par un dans l'espace temporaire du cloud, nettoyage après vérification.
- Historique durable des dépôts, projets, responsables, livrables, versions et liens Frame.io conservé indépendamment des fichiers vidéo.
- Suivi des projets et des paiements dans le dashboard Notion Engrame, selon son schéma actuel à vérifier.
- Une correction est une version du même livrable ; elle n'ajoute pas de montant à régler automatiquement. Attribution du travail et identité du déposant doivent rester deux informations distinctes.

## Premier essai concret

Ce paquet ne transfère aucun fichier. `preflight.py` vérifie les dossiers sources/destinations, un échantillon de dix fichiers et la capacité disque disponible. Il utilise uniquement des GET HTTPS et n'affiche aucun jeton ni corps de réponse en cas d'erreur.

1. Utiliser le nouvel environnement créé dans l'application Codex. Le chat cloud « Set up Mwac » a vérifié l'accès au dépôt `Bxndaa/Mwac` : il est vide, sans commit ni branche `main`. Initialiser ce dépôt avec les seuls fichiers de ce pilote puis relancer sa préparation. L'état publié de l'environnement reste à vérifier.
2. Copier `config.example.json` en `config.json` et y mettre les vrais identifiants des dossiers du pilote. La limite de 5 Gio de l'exemple est une valeur provisoire pour l'essai, pas une taille constatée.
3. Dans le nouvel environnement Codex Cloud, configurer les clés `ENGRAME_DRIVE_ACCESS_TOKEN` et `ENGRAME_FRAME_ACCESS_TOKEN` comme secrets réseau, respectivement limités à `www.googleapis.com` et `api.frame.io`. Les jetons d'accès servent seulement à cet essai ; leur renouvellement automatique est un préalable à l'exploitation. Vérifier que les clés sont disponibles pendant l'exécution du diagnostic. Ne jamais les copier dans le code, le dépôt ou un message.
4. Dans la tâche cloud, exécuter `python preflight.py --config config.json`. Le mode `--offline` mesure seulement le disque et valide la configuration sans appel distant.
5. Vérifier le résultat, puis essayer un export de test vers un dossier Frame.io identifié. Vérifier le téléchargement de l'original et sa taille avant tout nettoyage.
6. Tester une interruption et une reprise : pas de doublon, aucun nettoyage si l'envoi est incomplet, et conservation du suivi après retrait du fichier source.
7. Vérifier dans cette interface la possibilité d'enregistrer une tâche réellement cloud à intervalle de six heures. Les outils de planification disponibles dans ce chat local ne permettent pas d'activer ce planning cloud. Ne pas leur substituer une automatisation locale.

## Conditions avant activation

La capacité de disque réellement observée dans la VM est la référence. La documentation publique indique 32 Gio par tâche par défaut pour Pro/Business/Enterprise ; aucun quota personnel de 100 Go n'a été vérifié dans cette session.

La page web `chatgpt.com/codex/cloud/settings/environment/create` consultée ici utilise l'ancien assistant Codex Cloud. Sa liste de comptes vide ne décrit pas les accès du nouvel environnement de l'application. Dans cette ancienne expérience, les secrets sont retirés avant la phase agent ; les instructions ci-dessus sur les secrets réseau concernent le nouvel environnement et son coffre-fort personnel. Ne pas déplacer les secrets dans des variables ordinaires pour contourner cette différence.

Chaque nouveau chat cloud démarre depuis l'environnement publié avec ses propres fichiers. Un fichier SQLite local ne constitue donc pas à lui seul un historique commun entre plusieurs tâches. Le journal doit rester disponible entre les passages, par exemple dans les données du suivi Notion ou un petit journal privé sur Drive, avec des écritures de reprise testées. Cette option précise reste à choisir pendant le pilote.

Le réseau doit autoriser les API nécessaires ainsi que les hôtes HTTPS exacts des URLs d'upload signées retournées par Frame.io. Les identifiants Frame.io ne doivent jamais être envoyés aux hôtes d'upload. Aucun fichier Drive ne doit être rendu public pour permettre le transfert.

Prévoir un renouvellement stable des accès Google et Adobe : des jetons d'accès copiés une fois ne suffisent pas pour un planning autonome. Tester la planification, le renouvellement, la reprise et la conservation de l'historique dans le cloud avant de retirer des fichiers du Drive. Le premier nettoyage envisagé est la corbeille Drive, récupérable ; elle peut continuer à occuper du stockage jusqu'à sa purge. Aucune purge définitive n'est incluse dans ce pilote.

## Vérifications réalisées

- Documentation actuelle OpenAI sur les environnements, secrets réseau, ressources VM et tâches planifiées consultée.
- Interface web ancienne : assistant ouvert, aucun compte GitHub proposé dans la liste des organisations.
- Nouvel environnement de l'application : le chat « Set up Mwac » du 2 octobre confirme un accès GitHub en lecture à `Bxndaa/Mwac` et un dépôt vide. Publication et exécution du pilote non vérifiées.
- Contrats actuels Frame.io V4 : création d'upload local, envoi multipart et vérification via `upload_complete`/`upload_failed` consultés.
- Tests hors ligne du diagnostic inclus dans `test_preflight.py`.
- Aucun accès API authentifié Google/Frame.io testé ; aucun fichier vidéo téléchargé, envoyé ou supprimé.

## Sources

- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://learn.chatgpt.com/docs/environments/cloud-environment
- https://learn.chatgpt.com/docs/automations
- https://developers.google.com/workspace/drive/api/guides/manage-downloads
- https://next.developer.frame.io/platform/api-reference/files/create-local-upload
- https://next.developer.frame.io/platform/api-reference/files/show-file-upload-status

## Prochaine étape

Initialiser le dépôt vide et préparer le pilote dans l'environnement déjà créé. Vérifier la programmation cloud dans le compte, renseigner un seul dossier Drive et sa destination Frame.io, puis exécuter le diagnostic depuis la VM cloud. La synchronisation complète et le suivi financier restent à implémenter après validation de ces capacités.
