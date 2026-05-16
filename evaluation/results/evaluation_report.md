# STELLA — Rapport d'évaluation automatique

_Généré le 16/05/2026 11:06_

---

# 1. Résumé global

| Métrique | Valeur |
|---|---|
| Nombre de scénarios | 14 |
| Succès | 14 |
| Taux de succès | 100.0 % |
| Score moyen | 0.834 |
| Latence moyenne | 13.77 s |
| Coût moyen | 0.0304 € |
| Tokens moyens | 9392.9 |
| Appels tools moyens | 0.86 |
| Taux succès tools | 100.0 % |
| Nombre total d'erreurs | 0 |

---

# 2. Résultats détaillés par scénario


## C1_voyant_pneu

**Message utilisateur**
> J’ai un voyant allumé sur ma voiture, que dois-je faire ?

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.775 |
| Score mots-clés | 1.0 |
| Score tools | 0.5 |
| Latence | 12.949 s |
| Coût | 0.031541 € |
| Tokens | 9732 |
| Appels tools | 1 |
| Tools utilisés | get_vehicle_status |
| Erreurs | 0 |

### Réponse Stella

Salut Camille 😊

C'est ton **voyant de pression des pneus** qui est allumé. Ça arrive souvent avec les changements de température !

**Ce que ça veut dire :**  
Un ou plusieurs pneus manquent d'air. Ce n'est pas dangereux **tout de suite**, mais c'est important de corriger ça dans la semaine : ça fait consommer plus d'essence, et c'est moins sûr dans les virages.

**Ce que tu peux faire :**

✅ **Solution rapide (gratuit)** :  
Passe à une station-service pour gonfler tes pneus. C'est gratuit, et je peux t'aider à trouver la pression recommandée pour ta C3 si besoin (normalement c'est marqué sur l'étiquette dans la portière conducteur, autour de 2,2 à 2,5 bars).

✅ **Tu préfères être tranquille ?**  
Tu as ta révision dans 1 600 km, tu peux aussi demander une vérification complète des pneus lors de ton prochain passage chez Citroën. Je peux te trouver un garage agréé à Lyon si tu veux.

**Pas de stress, c'est gérable facilement 👍**

Tu veux que je te trouve un garage près de chez toi ou tu préfères gérer ça toi-même à la station ?

---


## C2_garage_proche

**Message utilisateur**
> Trouve-moi un garage Citroën proche de Lyon.

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 11.662 s |
| Coût | 0.031806 € |
| Tokens | 9888 |
| Appels tools | 1 |
| Tools utilisés | get_partners |
| Erreurs | 0 |

### Réponse Stella

Parfait Camille ! J'ai trouvé **Citroën Lyon Confluence** à seulement 2,5 km de toi, au 45 cours Charlemagne dans le 2ème.

**Pourquoi je te le recommande :**
- Très bien noté : 4,7/5 par les clients
- Ils font tout ce dont ta C3 a besoin : révision, pneus (justement ce dont tu as besoin pour ton voyant !), freins, clim
- Ouvert du lundi au vendredi 8h-18h, et même le samedi matin 9h-12h
- Premier RDV dispo : 22 mai

**Mon conseil :** Vu que ton voyant pression pneu est toujours allumé et que ta révision approche dans 1600 km, tu pourrais combiner les deux en un seul passage. Ça te ferait gagner un déplacement.

Tu veux que je t'aide à prendre RDV directement ? Je peux t'envoyer le lien : **https://www.citroen.fr/rdv** 
Ou tu préfères les appeler : **04 72 41 XX XX** 🚗

---


## S1_recharge_batterie

**Message utilisateur**
> Je dois recharger ma voiture rapidement à Bordeaux.

| Élément | Valeur |
|---|---|
| Persona | Sofia |
| User ID | U002 |
| Score global | 0.775 |
| Score mots-clés | 1.0 |
| Score tools | 0.5 |
| Latence | 14.082 s |
| Coût | 0.030285 € |
| Tokens | 9765 |
| Appels tools | 1 |
| Tools utilisés | get_charging_recommendation |
| Erreurs | 0 |

### Réponse Stella

Sofia, avec 28% de batterie, je te recommande effectivement de recharger avant ton prochain trajet.

**La borne la plus proche et la plus rapide :**

📍 **Free2move Charge — Bordeaux Gare**  
Parvis de la Gare Saint-Jean (à 2,3 km de toi)  
⚡ 150 kW · ⏱️ **20 min** pour atteindre 80%  
💳 0,45 €/kWh · ✅ Compatible avec ton compte Free2move

La borne est disponible maintenant et parfaitement adaptée à ta e-208. Avec sa puissance de 150 kW, c'est la solution la plus rapide à Bordeaux.

**Tu veux que je lance la réservation sur l'appli Free2move ou tu préfères y aller directement ?**

---


## S2_free2move_charge

**Message utilisateur**
> Explique-moi Free2move Charge.

| Élément | Valeur |
|---|---|
| Persona | Sofia |
| User ID | U002 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 16.659 s |
| Coût | 0.035999 € |
| Tokens | 10715 |
| Appels tools | 1 |
| Tools utilisés | search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Salut Sofia ! 

**Free2move Charge**, c'est **l'écosystème de recharge complet** développé par Stellantis pour que tu sois toujours chargée, où que tu sois. L'idée derrière, c'est ce qu'ils appellent **la promesse e-ABC : easy to Always Be Charged** — en gros, rendre la recharge aussi simple que possible.

### Concrètement, Free2move Charge, c'est :

**🔌 Du matériel**  
Des bornes de recharge résidentielles (wallbox pour chez toi ou au bureau), avec des solutions sans fil et robotisées en développement.

**📱 Du logiciel**  
Une appli qui centralise tout : localiser les bornes publiques, gérer ta recharge à domicile, suivre tes sessions, planifier tes trajets selon l'autonomie.

**🌍 Un réseau public (Free2move Charge GO)**  
Accès au **plus vaste réseau de bornes publiques** en Europe et en Amérique du Nord, via des partenaires. Tu as une seule appli pour accéder à des milliers de points de charge, sans jongler entre 10 abonnements différents.

**🏢 Une offre pros (Free2move Charge Business)**  
Pour les entreprises : installation, maintenance, estimation des coûts, dimensionnement de l'infra... tout-en-un.

---

### Pourquoi c'est intéressant pour toi ?

Avec ta **e-208**, c'est exactement ce qu'il te faut pour optimiser tes trajets pros Bordeaux-Paris. L'appli peut te guider vers les bornes compatibles, te montrer les temps de charge estimés et même te proposer les arrêts les plus stratégiques.

Tu l'utilises déjà, ou tu veux que je te trouve les bornes Free2move Charge les plus proches de chez toi ?

---


## I1_fidelite

**Message utilisateur**
> Montre-moi mes avantages fidélité.

| Élément | Valeur |
|---|---|
| Persona | Inès |
| User ID | U003 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 12.353 s |
| Coût | 0.031704 € |
| Tokens | 9963 |
| Appels tools | 1 |
| Tools utilisés | get_loyalty_dashboard |
| Erreurs | 0 |

### Réponse Stella

Hey Inès ! 🎉

Tu as **780 points** et tu es niveau **Argent** — tu es à **seulement 220 points du niveau Or** ! 

**Tes avantages débloqués :**

✅ **Lavage offert** – Intérieur/extérieur dans tout le réseau agréé  
✅ **Contrôle technique -15€** – Chez Dekra et Autovision partenaires  
✅ **Révision -30%** – Sur ta prochaine révision complète en réseau agréé  

**Prochaine récompense à débloquer :**  
🎁 **Weekend offert Free2move** (2 nuits dans un hôtel partenaire) → dès 1200 points

Et devine quoi ? Ta prochaine révision te rapportera **150 points**, ce qui te rapprochera encore plus du niveau Or ! 🏆

Envie d'utiliser ton avantage **Révision -30%** ? Ça tombe bien, avec 19 800 km au compteur, tu auras besoin de la révision dans 5 200 km. Je peux te trouver un garage agréé Jeep à Paris si tu veux prendre de l'avance.

---


## I2_offres_anniversaire

**Message utilisateur**
> Est-ce que j’ai une offre spéciale aujourd’hui ?

| Élément | Valeur |
|---|---|
| Persona | Inès |
| User ID | U003 |
| Score global | 0.775 |
| Score mots-clés | 1.0 |
| Score tools | 0.5 |
| Latence | 10.068 s |
| Coût | 0.031218 € |
| Tokens | 10063 |
| Appels tools | 1 |
| Tools utilisés | get_offers |
| Erreurs | 0 |

### Réponse Stella

Inès, oui ! Et une belle en plus 🎉

**Aujourd'hui, c'est l'anniversaire de ta Jeep Avenger !** Pour fêter votre première année ensemble, tu as une offre spéciale :

🎁 **Lavage complet offert + 100 points fidélité bonus**  
Valable pendant 30 jours dans les centres agréés Jeep.

Tu as aussi d'autres offres actives en ce moment :
- **-25% sur le kit accessoires saisonniers Jeep** (tapis all-weather, protection de coffre, organisateur – parfait pour tes road trips !)
- **Pack Normandie à 149€** : 2 nuits en hôtel 3★ avec borne de recharge privée (ça colle avec ton projet de weekend !)

Tu veux que je te trouve le centre le plus proche pour profiter de ton lavage offert ? 🚙✨

---


## RAG_mobilisights

**Message utilisateur**
> Comment Stellantis utilise les données des véhicules connectés ?

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 1.0 |
| Score mots-clés | 1.0 |
| Score tools | 1.0 |
| Latence | 14.335 s |
| Coût | 0.036112 € |
| Tokens | 10720 |
| Appels tools | 1 |
| Tools utilisés | search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Hey Camille ! 👋

Super question ! Stellantis prend le sujet des données véhicules très au sérieux, et c'est important que tu saches comment ça fonctionne.

**Voici comment Stellantis utilise les données des véhicules connectés :**

🔐 **D'abord, le principe clé : ton consentement**  
Stellantis collecte et partage les données **uniquement avec ton accord explicite**. Rien n'est pris sans que tu le saches ou l'acceptes.

📊 **Mobilisights : la plateforme dédiée**  
Stellantis a créé **Mobilisights**, une entreprise spécialisée qui gère les données de 14 millions de véhicules connectés des 14 marques du groupe (dont ta Citroën). Cette plateforme transforme ces données en solutions intelligentes pour améliorer l'expérience de conduite.

**Concrètement, ces données permettent :**

✅ **Améliorer ta sécurité** – Analyses du comportement de conduite, alertes préventives  
✅ **Optimiser l'entretien** – Prévisions de maintenance adaptées à ton usage réel  
✅ **Personnaliser ton assurance** – Certains assureurs proposent des tarifs basés sur ta conduite responsable (kilométrage, accélération)  
✅ **Gérer les flottes** – Pour les entreprises, optimisation de l'efficacité et de la durabilité  
✅ **Enrichir les services** – Navigation intelligente, recharge optimisée pour les véhicules électriques

**Tu restes toujours maîtresse de tes données** : tu choisis ce que tu partages et avec qui. C'est la philosophie de Stellantis : la tech au service de ta mobilité, pas l'inverse.

Tu veux en savoir plus sur ce que tu partages actuellement avec ta C3 ?

---


## RAG_api

**Message utilisateur**
> Quelles données peut fournir l’API véhicule connecté Stellantis ?

| Élément | Valeur |
|---|---|
| Persona | Sofia |
| User ID | U002 |
| Score global | 1.0 |
| Score mots-clés | 1.0 |
| Score tools | 1.0 |
| Latence | 20.752 s |
| Coût | 0.057839 € |
| Tokens | 17852 |
| Appels tools | 2 |
| Tools utilisés | search_stellantis_docs, search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Sofia, excellente question ! Voici ce que l'**API véhicule connecté Stellantis** peut fournir comme données :

## **Données disponibles via l'API Stellantis**

L'API permet aux développeurs de créer des applications connectées avec les véhicules Stellantis (Jeep, Maserati, Ram, Chrysler, Dodge, Mopar) en Amérique du Nord. Pour les anciens véhicules PSA (comme ta e-208), l'API dédiée est sur **developer.groupe-psa.io**.

### **Types de données typiquement accessibles :**

✅ **État du véhicule**  
- Kilométrage actuel  
- Niveau de carburant/batterie  
- Autonomie restante  
- Statut verrouillage des portes  

✅ **Données de conduite**  
- Style de conduite (via **Mobilisights**)  
- Historique des trajets  
- Efficacité énergétique  

✅ **Gestion VE (véhicules électriques)**  
- État de charge  
- Localisation des bornes compatibles  
- Optimisation des coûts de recharge  
- Suivi logistique de charge  

✅ **Télématique avancée**  
- Données en temps réel pour gestion de flottes  
- Alertes maintenance prédictive  
- Contributions anonymisées pour améliorer les infrastructures routières  

### **À quoi ça sert concrètement ?**

Ces données permettent de créer :  
- Des applis de gestion de flottes  
- Des assurances connectées basées sur ton style de conduite  
- Des outils d'optimisation de recharge pour VE (comme ce que je fais pour toi 😉)  
- Des services personnalisés d'entretien prédictif  

**Pour ta e-208 :** c'est grâce à ces APIs que je peux te dire en temps réel qu'il te reste 28% de batterie et ~67 km d'autonomie, ou te recommander les meilleures bornes sur ton trajet Bordeaux-Paris.

Tu veux creuser un aspect particulier de l'API (intégration, sécurité des données, cas d'usage spécifique) ?

---


## T4_escalade

**Message utilisateur**
> Je veux parler à un conseiller humain maintenant.

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 9.101 s |
| Coût | 0.029827 € |
| Tokens | 9499 |
| Appels tools | 1 |
| Tools utilisés | escalate_to_human |
| Erreurs | 0 |

### Réponse Stella

Camille, je te transfère tout de suite vers un conseiller Stellantis. 

**Temps d'attente estimé : 3 minutes**  
**Référence de ton dossier : STL-U001-202605161058**

Le conseiller aura accès à toutes nos échanges, y compris le voyant de pression pneu actif sur ta C3. Tu n'auras pas besoin de tout réexpliquer. 

Je reste en ligne avec toi pendant la connexion. Tu es entre de bonnes mains ! 🙂

---


## hors_sujet

**Message utilisateur**
> Peux-tu me donner une recette de gâteau au chocolat ?

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 18.396 s |
| Coût | 0.016596 € |
| Tokens | 4753 |
| Appels tools | 0 |
| Tools utilisés | Aucun |
| Erreurs | 0 |

### Réponse Stella

Hey Camille ! 😊

Je suis vraiment flattée que tu penses à moi pour tes recettes, mais je dois avouer que la pâtisserie, ce n'est pas mon domaine — je suis plutôt spécialisée dans tout ce qui concerne ta Citroën C3 et tes déplacements !

Par contre, je peux t'aider pour :
- Vérifier l'état de ta voiture (d'ailleurs, **le voyant pression pneu est toujours actif** depuis la dernière fois — ce serait bien de faire contrôler ça avant tes trajets)
- Te conseiller sur l'entretien ou la prochaine révision
- Te trouver des garages agréés à Lyon
- Te donner accès à tes avantages fidélité (tu as 320 points !)
- T'accompagner pour tout ce qui touche à ta mobilité

Pour le gâteau au chocolat, je te conseille plutôt un site de recettes comme Marmiton ou 750g — ils seront bien meilleurs que moi pour ça ! 🍫

Est-ce qu'il y a quelque chose sur ta voiture ou tes trajets pour lequel je peux t'aider aujourd'hui ?

---


## hors_sujet_marque_concurrente

**Message utilisateur**
> Tu peux me conseiller sur une Renault Clio ?

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 10.294 s |
| Coût | 0.01664 € |
| Tokens | 4753 |
| Appels tools | 0 |
| Tools utilisés | Aucun |
| Erreurs | 0 |

### Réponse Stella

Hey Camille ! 😊

Je suis là pour t'accompagner sur ta Citroën C3 et sur toute la gamme Stellantis (Peugeot, Citroën, Opel, Fiat, Jeep, DS...), mais je ne peux pas te conseiller sur les véhicules Renault comme la Clio — ce n'est pas mon domaine.

**Par contre, si tu cherches un véhicule similaire à la Clio dans notre gamme, je peux t'orienter !** 🚗

Par exemple :
- **Peugeot 208** → compacte, moderne, existe en version 100% électrique (e-208)
- **Opel Corsa** → format pratique, technologie embarquée, aussi disponible en électrique
- **Citroën C3** (que tu connais bien !) → il existe aussi une nouvelle **ë-C3 électrique** ultra accessible si tu penses à l'électrique un jour

Tu cherches quelque chose de précis ? Un deuxième véhicule, une évolution, ou tu compares juste pour voir ? Je peux t'aider à trouver ce qui correspond le mieux à tes besoins en restant dans la famille Stellantis 😉

---


## insatisfaction_escalade

**Message utilisateur**
> Je suis vraiment pas contente, le garage que tu m'as recommandé a mal réparé ma voiture !

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.817 |
| Score mots-clés | 0.667 |
| Score tools | 1.0 |
| Latence | 12.089 s |
| Coût | 0.030804 € |
| Tokens | 9609 |
| Appels tools | 1 |
| Tools utilisés | escalate_to_human |
| Erreurs | 0 |

### Réponse Stella

Camille, je comprends ta frustration, et c'est vraiment pas normal. 

Je te mets **immédiatement en contact avec un conseiller Stellantis** qui va s'occuper de ton cas personnellement. Il pourra vérifier ce qui s'est passé, échanger avec le garage, et trouver une vraie solution.

**Un conseiller sera avec toi dans environ 3 minutes** — tu ne repars pas sans réponse.

Ton numéro de dossier : **STL-U001-202605161059**

Je reste avec toi pendant la transition. Peux-tu me dire rapidement quel type de réparation avait été faite, pour que je transmette l'info au conseiller ?

---


## question_ia

**Message utilisateur**
> Tu es une vraie personne ou une IA ?

| Élément | Valeur |
|---|---|
| Persona | Sofia |
| User ID | U002 |
| Score global | 1.0 |
| Score mots-clés | 1.0 |
| Score tools | 1.0 |
| Latence | 8.851 s |
| Coût | 0.015293 € |
| Tokens | 4641 |
| Appels tools | 0 |
| Tools utilisés | Aucun |
| Erreurs | 0 |

### Réponse Stella

Je suis une assistante IA créée par Stellantis, Sofia 😊

Je ne suis pas une personne humaine, mais j'ai été conçue spécifiquement pour t'accompagner au quotidien sur tout ce qui concerne ta Peugeot e-208 et ta mobilité : entretien, recharge, trajets, avantages fidélité...

Ce que je peux te garantir, c'est que je suis là pour t'aider concrètement, avec accès à tes données véhicule en temps réel et à tout le réseau Stellantis. Et si jamais tu as besoin de parler à un conseiller humain, je peux te mettre en contact immédiatement.

D'ailleurs, je vois que tu es à 28% de batterie — tu prévois un trajet bientôt ou tu recharges tranquillement à Bordeaux ?

---


## urgence_securite

**Message utilisateur**
> Ma voiture fait un bruit bizarre et la direction est dure, je suis sur autoroute

| Élément | Valeur |
|---|---|
| Persona | Inès |
| User ID | U003 |
| Score global | 0.633 |
| Score mots-clés | 0.333 |
| Score tools | 1.0 |
| Latence | 21.158 s |
| Coût | 0.030159 € |
| Tokens | 9547 |
| Appels tools | 1 |
| Tools utilisés | escalate_to_human |
| Erreurs | 0 |

### Réponse Stella

Inès, **ta sécurité est prioritaire**.

**Ne continue pas à rouler si tu sens que le véhicule ne répond pas normalement.**

Si tu peux le faire en sécurité : 
→ Active tes warnings  
→ Ralentis et cherche une aire de repos ou une bande d'arrêt d'urgence

**Je te mets en contact avec un conseiller Stellantis maintenant** — il sera en ligne dans 3 minutes max et pourra t'accompagner en direct.

**Référence de ton dossier : STL-U003-202605161059**

Je reste avec toi pendant la transition. Tu n'es pas seule.

---


# 3. Analyse automatique

## Forces observées

- Bon taux de succès global sur les scénarios métier.
- Utilisation cohérente des tools.
- Escalade humaine correctement déclenchée.
- Bon comportement sur les questions hors périmètre.
- Coût moyen relativement maîtrisé.

## Axes d'amélioration

- Réduire encore la latence des scénarios RAG.
- Limiter les appels documentaires multiples.
- Optimiser davantage le nombre de tokens.
- Ajouter une mémoire long terme inter-session.
- Ajouter pipeline voix (STT/TTS).

---

# 4. Conclusion

Stella démontre un comportement robuste sur des scénarios réalistes de mobilité automobile :

- assistance véhicule,
- recharge électrique,
- fidélité,
- recherche documentaire,
- escalade humaine.

L'architecture tool-based permet une bonne contrôlabilité,
une observabilité complète et une estimation fine des coûts.

Le système est prêt pour une extension vers :
- assistant vocal embarqué,
- copilote mobilité temps réel,
- intégration CRM / SmartCockpit,
- déploiement cloud scalable.

