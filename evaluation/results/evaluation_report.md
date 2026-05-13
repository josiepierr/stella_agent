# STELLA — Rapport d'évaluation automatique

_Généré le 13/05/2026 17:28_

---

# 1. Résumé global

| Métrique | Valeur |
|---|---|
| Nombre de scénarios | 10 |
| Succès | 10 |
| Taux de succès | 100.0 % |
| Score moyen | 0.827 |
| Latence moyenne | 15.35 s |
| Coût moyen | 0.0327 € |
| Tokens moyens | 10081.9 |
| Appels tools moyens | 1 |
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
| Latence | 17.381 s |
| Coût | 0.031089 € |
| Tokens | 9528 |
| Appels tools | 1 |
| Tools utilisés | get_vehicle_status |
| Erreurs | 0 |

### Réponse Stella

Salut Camille ! 👋

C'est ton voyant de **pression des pneus** qui est allumé — on en avait déjà parlé la dernière fois. Pas d'inquiétude, ce n'est pas une urgence, mais **c'est important de s'en occuper cette semaine**.

**Pourquoi ?**  
Un pneu sous-gonflé, c'est :
- Une consommation de carburant plus élevée
- Une tenue de route moins bonne, surtout dans les virages
- Une usure plus rapide du pneu

**Ce que tu peux faire :**

**Option 1 — La plus simple**  
Passe à une **station-service** (Total, BP, etc.) et utilise la borne de gonflage (c'est gratuit). Les pressions recommandées pour ta C3 sont indiquées sur une étiquette dans le montant de la portière conducteur (souvent autour de 2.2 bars).

**Option 2 — Tu préfères déléguer**  
Je peux te trouver un garage Citroën agréé à Lyon qui vérifiera ça gratuitement ou pour quelques euros. Veux-tu que je te trouve une adresse proche de chez toi ?

**Action concrète :** Si tu passes devant une station cette semaine, prends 5 minutes pour gonfler tes pneus. Ça te fera économiser du carburant dès maintenant ! 🚗

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
| Latence | 14.623 s |
| Coût | 0.030871 € |
| Tokens | 9649 |
| Appels tools | 1 |
| Tools utilisés | get_partners |
| Erreurs | 0 |

### Réponse Stella

Camille, j'ai trouvé **Citroën Lyon Confluence** à seulement 2,5 km de toi !

📍 **45 cours Charlemagne, Lyon 2**  
☎️ **04 72 41 XX XX**  
🕒 **Lun-Ven 8h-18h, Sam 9h-12h**  
⭐ **Note : 4,7/5**

Ils proposent :
✔️ Révisions  
✔️ Pneus (pratique pour ton voyant de pression !)  
✔️ Freins, climatisation, CT partenaire  

Le prochain créneau disponible est **le 8 mai** selon le système.

Tu veux que je t'envoie le lien pour réserver ton RDV directement en ligne ? 🚗  
[📲 Réserver ici](https://www.citroen.fr/rdv)

Ça te permettrait de régler à la fois le voyant pneu et de te rapprocher de ta prochaine révision (dans 1600 km).

---


## S1_recharge_batterie

**Message utilisateur**
> Je dois recharger ma voiture rapidement à Bordeaux.

| Élément | Valeur |
|---|---|
| Persona | Sofia |
| User ID | U002 |
| Score global | 0.638 |
| Score mots-clés | 0.75 |
| Score tools | 0.5 |
| Latence | 10.046 s |
| Coût | 0.029444 € |
| Tokens | 9536 |
| Appels tools | 1 |
| Tools utilisés | get_charging_recommendation |
| Erreurs | 0 |

### Réponse Stella

Sofia, avec 28% de batterie restante, je te recommande la **borne Free2move Charge à Bordeaux Gare** — elle est à seulement 2,3 km de toi, parvis de la Gare Saint-Jean.

**Ce qui est intéressant :**
- Puissance : 150 kW (charge rapide)
- Temps estimé : **20 minutes** pour atteindre 80%
- Tarif : 0,45 €/kWh
- Compatible avec ton compte Free2move
- Disponible maintenant ✅

Vu que tu es à 67 km d'autonomie, tu peux y aller tranquillement. 

**Je lance la navigation vers cette borne ou tu préfères la réserver directement via l'app Free2move Charge ?**

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
| Latence | 18.419 s |
| Coût | 0.034619 € |
| Tokens | 10447 |
| Appels tools | 1 |
| Tools utilisés | search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Sofia, **Free2move Charge**, c'est l'écosystème de recharge complet de Stellantis, conçu pour que tu ne sois jamais à court de batterie. 🔋

**Concrètement, ça veut dire quoi ?**

C'est une solution tout-en-un qui combine **3 piliers** :

🔌 **Du matériel** : bornes de recharge à domicile ou en entreprise, avec de futures options comme la recharge sans fil ou par robot inductif (oui, ça arrive !)

📱 **Du logiciel** : une appli qui te permet de localiser les bornes publiques, de gérer ta recharge, et d'optimiser tes coûts énergétiques

⚡ **Des services** : installation, maintenance, accès au plus large réseau de bornes publiques via des partenaires en Europe et en Amérique du Nord

**La promesse e-ABC : "easy to Always Be Charged"**  
L'idée, c'est que tu n'aies plus à te demander *où* ni *comment* recharger. Free2move Charge s'occupe de tout, chez toi comme sur la route.

---

**Pour toi et ta e-208 :**  
Tu peux utiliser **Free2move Charge GO** pour accéder à un réseau ultra-large de bornes publiques partout en Europe, avec un seul compte et une facturation unifiée. Vu que tu fais souvent des trajets pros comme Bordeaux-Paris, ça simplifie vraiment la vie.

Tu veux que je te montre comment activer Free2move Charge GO, ou tu préfères des infos sur l'installation d'une borne à domicile ?

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
| Latence | 13.585 s |
| Coût | 0.031969 € |
| Tokens | 9811 |
| Appels tools | 1 |
| Tools utilisés | get_loyalty_dashboard |
| Erreurs | 0 |

### Réponse Stella

Super Inès ! Voici où tu en es 🎉

**780 points · Niveau Argent**  
Plus que **420 points** pour passer au niveau Or et débloquer le **weekend offert Free2move** (2 nuits en hôtel partenaire).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✅ Tes avantages disponibles tout de suite :**

🧼 **Lavage offert**  
→ Intérieur/extérieur dans tous les garages agréés  

🔧 **Contrôle technique -15€**  
→ Valable chez Dekra et Autovision partenaires  

⚙️ **Révision -30%**  
→ Sur ta prochaine révision complète en réseau agréé  

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💡 Comment gagner des points :**  
Ta prochaine révision arrive dans 5200 km, elle te rapportera **+150 points**.

Vu que tu prévois un road trip ce weekend, c'est le moment parfait pour profiter de ta **révision à -30%** avant de partir. Tu combines l'utile à l'agréable, et tu passes le cap des 1000 points ! 🚗✨

Tu veux que je te trouve un garage agréé Jeep à Paris pour programmer ça ?

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
| Latence | 14.771 s |
| Coût | 0.031345 € |
| Tokens | 9901 |
| Appels tools | 1 |
| Tools utilisés | get_offers |
| Erreurs | 0 |

### Réponse Stella

🎉 **Inès, devine quoi ? C'est un jour spécial !**

Aujourd'hui, c'est l'anniversaire de ta Jeep Avenger — **1 an ensemble** ! Et pour fêter ça, j'ai une **offre exclusive** pour toi :

🎁 **Cadeau anniversaire véhicule**  
→ Un lavage complet offert + 100 points bonus fidélité  
→ Valable pendant 30 jours (jusqu'au 4 juin)

Parfait pour bichonner ta Jeep avant ce road trip en Normandie qu'on avait évoqué, non ? 

Et en plus, j'ai repéré quelques autres offres qui pourraient te plaire :
- **-25% sur le kit accessoires Jeep** (tapis all-weather, protection coffre — pile pour l'aventure)
- **Road trip Normandie** : pack 2 nuits + borne privée à partir de 149€

Envie de profiter du lavage offert ? Je peux te trouver un garage partenaire près de chez toi à Paris. 🚗✨

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
| Latence | 16.842 s |
| Coût | 0.035593 € |
| Tokens | 10516 |
| Appels tools | 1 |
| Tools utilisés | search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Hey Camille ! 👋

Super question — je vais t'expliquer comment Stellantis utilise les données des véhicules connectés de manière simple et transparente.

## 🔐 **Le principe fondamental : ton consentement d'abord**

Stellantis collecte et partage les données de ton véhicule **uniquement avec ton accord explicite**. Tu gardes le contrôle, toujours.

## 📊 **Mobilisights : la plateforme de données**

Stellantis a créé **Mobilisights**, une filiale dédiée qui centralise les données télématiques de **14 millions de véhicules connectés** à travers les 14 marques du groupe (dont Citroën, Peugeot, Jeep, Fiat, etc.).

### **À quoi servent ces données ?**

Elles permettent de créer des **solutions intelligentes** pour améliorer :
- **La sécurité** (détection d'incidents, alertes préventives)
- **L'efficacité** (optimisation des trajets, maintenance prédictive)
- **Ton expérience** (services personnalisés, assistance en temps réel)

Mobilisights travaille avec des partenaires pour développer des services comme :
- Assurances adaptées à ta conduite
- Gestion de flottes pour professionnels
- Prévention et assistance routière

## 🎯 **Concrètement pour toi**

Les données de ta C3 (kilométrage, alertes comme ton voyant pression pneu, habitudes de conduite) servent à **te proposer des recommandations personnalisées** : rappels d'entretien au bon moment, bornes de recharge proches si tu passes à l'électrique, offres ciblées.

**Rien n'est utilisé sans que tu aies dit oui.**

Tu veux en savoir plus sur un aspect précis, ou voir comment gérer tes préférences de données ?

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
| Latence | 22.437 s |
| Coût | 0.055942 € |
| Tokens | 17465 |
| Appels tools | 2 |
| Tools utilisés | search_stellantis_docs, search_stellantis_docs |
| Erreurs | 0 |

### Réponse Stella

Sofia, bonne question ! L'**API véhicule connecté Stellantis** permet aux développeurs et partenaires d'accéder à de nombreuses données en temps réel issues de véhicules connectés.

Voici ce que l'API peut fournir, selon la documentation officielle :

## **📊 Données principales disponibles**

**Données de base :**
- **Kilométrage** (odomètre)
- **Position GPS** et localisation
- **État du carburant ou de la batterie** (niveau, autonomie)
- **État du véhicule** (portes, serrures, capot, alarme)
- **Température** et conditions environnementales

**Données de conduite :**
- **Accélération** et style de conduite
- **Historique des trajets**
- **Comportement routier** (utilisé par exemple pour l'assurance connectée)

**Données pour véhicules électriques :**
- **État de charge de la batterie** en temps réel
- **Gestion de la recharge** (via streaming de données)
- **Optimisation des cycles de charge**

---

## **🔗 Applications concrètes**

Ces données sont utilisées par :
- **Gestionnaires de flottes** → suivi des véhicules, optimisation des opérations
- **Assureurs connectés** → tarifs personnalisés selon le style de conduite
- **Fournisseurs de services télématiques** → maintenance prédictive, assistance
- **Partenaires mobilité électrique** → gestion de la recharge intelligente

---

## **💡 Pour ton e-208**

Concrètement, c'est grâce à cette API que je peux te donner l'état de ta batterie (28% actuellement), ton kilométrage précis (41 200 km), et te recommander les meilleures bornes sur tes trajets pros Bordeaux-Paris.

Tu cherches à intégrer ces données dans une application ou un service spécifique ? 🚗⚡

---


## T4_escalade

**Message utilisateur**
> Je veux parler à un conseiller humain maintenant.

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 1.0 |
| Score mots-clés | 1.0 |
| Score tools | 1.0 |
| Latence | 15.722 s |
| Coût | 0.029493 € |
| Tokens | 9314 |
| Appels tools | 1 |
| Tools utilisés | escalate_to_human |
| Erreurs | 0 |

### Réponse Stella

Bien sûr, Camille ! Je te mets en contact avec un conseiller Stellantis tout de suite.

**Temps d'attente estimé : 3 minutes**  
**Référence de ton dossier : STL-U001-202605131714**

Le conseiller aura accès à tout le contexte de notre échange, y compris l'historique de ton voyant de pression des pneus. Tu n'auras pas besoin de tout réexpliquer.

Je reste en ligne pendant la transition. Tu ne repars pas sans réponse. 💙

---


## hors_sujet

**Message utilisateur**
> Peux-tu me donner une recette de gâteau au chocolat ?

| Élément | Valeur |
|---|---|
| Persona | Camille |
| User ID | U001 |
| Score global | 0.633 |
| Score mots-clés | 0.333 |
| Score tools | 1.0 |
| Latence | 9.62 s |
| Coût | 0.016383 € |
| Tokens | 4652 |
| Appels tools | 0 |
| Tools utilisés | Aucun |
| Erreurs | 0 |

### Réponse Stella

Hey Camille ! 😊

Je suis vraiment flattée que tu penses à moi pour ça, mais je dois t'avouer que la pâtisserie, c'est pas du tout mon rayon ! Je suis spécialisée dans tout ce qui touche à ta Citroën C3 et à ta mobilité : entretien, trajets, avantages fidélité, bornes de recharge...

Par contre, ce que je peux faire pour toi aujourd'hui :

**🔧 On pourrait régler ce voyant de pression pneu qui est toujours actif** – je vois que tu n'as pas encore pris le RDV qu'on t'avait proposé la dernière fois. C'est vraiment important pour ta sécurité, surtout avec l'hiver qui arrive à Lyon.

Je peux te trouver un garage agréé Citroën près de chez toi et vérifier si tu as des offres dispo avec tes 320 points fidélité ?

Sinon, pour ta recette de gâteau, je te conseille un bon site de cuisine ou même YouTube – tu trouveras des recettes super simples à suivre ! 🍫

Qu'est-ce que tu préfères qu'on fasse pour ta C3 ?

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

