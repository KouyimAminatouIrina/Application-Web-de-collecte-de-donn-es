"""
seed_data.py — Peuplement de la base MecZone avec des données réalistes
Sources : garageautomobiledouala.com, actucameroun.com, carcameroun.com,
          allafrica.com, voaafrique.com, jeuneafrique.com, camer.be

Contextes par ville :
  Douala     → chaleur (35°C), humidité atlantique, embouteillages denses
  Yaoundé    → trafic dense, routes secondaires dégradées, saison des pluies
  Limbé      → humidité saline côtière, corrosion accélérée
  Buea       → flancs du mont Cameroun, pentes fortes, brouillard
  Bafoussam  → hauts plateaux, axe Douala-Bafoussam accidentogène
  Garoua     → chaleur extrême 40°C+, poussière sahélienne, RN1 dégradée
  Ngaoundéré → altitude 1100m, savane-montagne, traversée urbaine trouée
  Maroua     → Extrême-Nord, 40-45°C, sable, harmattan
  Ebolowa    → forêt équatoriale, humidité permanente, pistes en terre

Usage :
    export DATABASE_URL='postgresql://user:password@host/dbname'
    python seed_data.py
"""

import os
import psycopg2
from datetime import datetime, timedelta
import random
from collections import Counter

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


REPORTS = [

    # ═══════════════ DOUALA ═══════════════
    {
        "name": "Hervé", "city": "Douala", "vehicle_model": "Toyota Corolla", "vehicle_year": 2008,
        "problem_description": "La batterie se décharge très vite, la voiture ne démarre plus le matin après seulement 2 ans d'utilisation.",
        "cause": "La chaleur intense de Douala (60-70°C dans le compartiment moteur) accélère l'évaporation de l'électrolyte et corrode les plaques. L'usage permanent de la climatisation aggrave la décharge.",
        "solution": "Remplacez la batterie par un modèle adapté aux pays chauds (AGM ou calcium-calcium). Nettoyez les bornes. Vérifiez l'alternateur.",
    },
    {
        "name": "Sandrine", "city": "Douala", "vehicle_model": "Toyota Corolla", "vehicle_year": 2010,
        "problem_description": "Le moteur surchauffe dans les embouteillages de Bonabéri, la jauge de température monte dans le rouge.",
        "cause": "Dans les embouteillages de Douala, le moteur tourne sans refroidissement par mouvement. Avec 35°C ambiants et la clim à fond, la température monte dangereusement. Fuite probable de liquide de refroidissement.",
        "solution": "Arrêtez immédiatement, coupez la clim et mettez le chauffage à fond. Vérifiez le liquide de refroidissement et les joints. La réparation d'une culasse déformée coûte 300 000 à 500 000 FCFA.",
    },
    {
        "name": "Patrice", "city": "Douala", "vehicle_model": "Nissan Almera", "vehicle_year": 2005,
        "problem_description": "Les freins grincent et la pédale descend au fond, surtout dans les descentes vers Akwa.",
        "cause": "Les embouteillages quotidiens de Douala provoquent une usure intensive des plaquettes. 90% des véhicules doivent remplacer leurs plaquettes avant 50 000 km ici.",
        "solution": "Vérifiez immédiatement l'épaisseur des plaquettes et le niveau de liquide de frein. Remplacez les plaquettes usées et contrôlez les disques.",
    },
    {
        "name": "Carine", "city": "Douala", "vehicle_model": "Honda CR-V", "vehicle_year": 2007,
        "problem_description": "La climatisation ne refroidit plus, le compresseur fait un bruit bizarre.",
        "cause": "L'humidité côtière et les températures élevées provoquent des fuites fréquentes dans le circuit de climatisation, surtout au niveau du compresseur.",
        "solution": "Faites recharger le gaz réfrigérant R134a (15 000 à 30 000 FCFA). Vérifiez les fuites du circuit et l'état du compresseur. Nettoyez le condenseur.",
    },
    {
        "name": "Blaise", "city": "Douala", "vehicle_model": "Toyota Land Cruiser", "vehicle_year": 2003,
        "problem_description": "La suspension fait des bruits métalliques sur les routes de Bonabéri, le volant vibre en roulant.",
        "cause": "Les nids-de-poule omniprésents de Douala détruisent amortisseurs, biellettes et silentblocs. Les amortisseurs en fin de vie produisent ce claquement sourd caractéristique.",
        "solution": "Inspectez les amortisseurs, les silentblocs et les rotules. Remplacez les pièces défaillantes. Contrôlez les amortisseurs tous les 10 000 km.",
    },
    {
        "name": "Aristide", "city": "Douala", "vehicle_model": "Renault Logan", "vehicle_year": 2012,
        "problem_description": "Le moteur perd de la puissance et fume un peu en montée, surtout chargé.",
        "cause": "La chaleur excessive et la qualité du carburant encrassent rapidement les injecteurs. La surcharge fréquente aggrave la perte de puissance.",
        "solution": "Faites un décalaminage moteur et nettoyez les injecteurs. Changez le filtre à air et à carburant. Utilisez du carburant de qualité supérieure.",
    },
    {
        "name": "Marguerite", "city": "Douala", "vehicle_model": "Peugeot 207", "vehicle_year": 2011,
        "problem_description": "Les pneus s'usent très vite et de façon irrégulière, crevaisons fréquentes.",
        "cause": "Les nids-de-poule de Douala provoquent une usure irrégulière accélérée. Les conducteurs doivent renouveler leurs pneus deux fois plus souvent qu'ailleurs.",
        "solution": "Contrôlez la pression chaque semaine. Faites aligner et équilibrer les roues régulièrement. Optez pour des pneus Dunlop Grandtrek ou Michelin LTX.",
    },
    {
        "name": "Fernand", "city": "Douala", "vehicle_model": "Mitsubishi Pajero", "vehicle_year": 2006,
        "problem_description": "L'alternateur ne charge plus, toutes les lumières du tableau de bord s'allument.",
        "cause": "L'humidité côtière de Douala accélère la corrosion des connexions électriques et l'usure du régulateur d'alternateur.",
        "solution": "Testez l'alternateur (doit donner 13,5 à 14,5V moteur tournant). Remplacez l'alternateur défaillant et vérifiez le câblage électrique.",
    },

    # ═══════════════ YAOUNDÉ ═══════════════
    {
        "name": "Christelle", "city": "Yaoundé", "vehicle_model": "Toyota Corolla", "vehicle_year": 2009,
        "problem_description": "Les freins s'usent très vite, bruit de frottement dès que j'appuie sur la pédale.",
        "cause": "Les embouteillages de Yaoundé usent les freins rapidement. La poussière et la boue des saisons des pluies encrassent les étriers.",
        "solution": "Remplacez les plaquettes de frein (usure avant 50 000 km attendue). Nettoyez les étriers et vérifiez les disques.",
    },
    {
        "name": "Théodore", "city": "Yaoundé", "vehicle_model": "Hyundai Accent", "vehicle_year": 2014,
        "problem_description": "La batterie ne tient plus la charge, le voyant batterie est allumé en permanence.",
        "cause": "La chaleur réduit la durée de vie des batteries de 40%. Les embouteillages en côte épuisent rapidement une batterie affaiblie.",
        "solution": "Testez la batterie et l'alternateur. Remplacez la batterie si elle a plus de 2 ans. Nettoyez les cosses corrodées.",
    },
    {
        "name": "Élisabeth", "city": "Yaoundé", "vehicle_model": "Toyota Hilux", "vehicle_year": 2004,
        "problem_description": "La suspension est très molle, la voiture oscille beaucoup sur les routes secondaires d'Obili.",
        "cause": "Les routes secondaires de Yaoundé, très dégradées après chaque saison des pluies, détruisent les amortisseurs. La moitié des voitures ont des suspensions défaillantes avant 80 000 km.",
        "solution": "Remplacez les amortisseurs et vérifiez les silentblocs. Contrôlez les amortisseurs tous les 10 000 km.",
    },
    {
        "name": "Roger", "city": "Yaoundé", "vehicle_model": "Peugeot 406", "vehicle_year": 2003,
        "problem_description": "Le moteur cliquète au démarrage et consomme beaucoup d'huile.",
        "cause": "Moteur âgé avec joints et segments usés. La qualité variable des lubrifiants disponibles accélère l'usure des véhicules anciens.",
        "solution": "Vérifiez le niveau et la qualité de l'huile moteur. Faites une vidange avec une huile adaptée (5W40). Diagnostiquez avec un professionnel.",
    },
    {
        "name": "Solange", "city": "Yaoundé", "vehicle_model": "Nissan X-Trail", "vehicle_year": 2015,
        "problem_description": "Le système d'injection a un problème, la voiture cale parfois à froid.",
        "cause": "L'injection directe est très sensible à la qualité du carburant. L'eau de condensation dans le réservoir et les carburants de qualité variable endommagent pompe, rampe et injecteurs.",
        "solution": "Utilisez un nettoyant pour injecteurs. Faites un diagnostic électronique complet. Remplacez le filtre à carburant.",
    },
    {
        "name": "Jean-Pierre", "city": "Yaoundé", "vehicle_model": "Toyota Fortuner", "vehicle_year": 2017,
        "problem_description": "La direction est dure et fait un bruit de grincement dans les virages.",
        "cause": "Les nids-de-poule des axes secondaires de Yaoundé usent rapidement les rotules de direction et les bras de direction, souvent désarticulés.",
        "solution": "Vérifiez les rotules de direction, les biellettes et le niveau d'huile de direction assistée. Une rotule usée est dangereuse — intervenez rapidement.",
    },
    {
        "name": "Bernadette", "city": "Yaoundé", "vehicle_model": "Renault Clio", "vehicle_year": 2016,
        "problem_description": "Le pot catalytique est encrassé, l'échappement fume beaucoup.",
        "cause": "Les carburants de qualité variable encrassent rapidement le catalyseur. L'utilisation fréquente en ville à bas régime aggrave le problème.",
        "solution": "Faites un décalaminage. Si le catalyseur est définitivement encrassé, remplacez-le. Utilisez du carburant de meilleure qualité.",
    },

    # ═══════════════ LIMBÉ ═══════════════
    {
        "name": "Victor", "city": "Limbé", "vehicle_model": "Toyota RAV4", "vehicle_year": 2010,
        "problem_description": "La carrosserie rouille rapidement, des points de rouille sous les portières en moins d'un an.",
        "cause": "L'air marin chargé en sel de Limbé attaque la carrosserie et les parties métalliques. La rouille progresse très vite dans cet environnement côtier volcanique.",
        "solution": "Appliquez une protection anticorrosion sur le dessous de caisse chaque année. Lavez régulièrement le dessous du véhicule à grande eau. Traitez les points de rouille avec un convertisseur.",
    },
    {
        "name": "Ngono", "city": "Limbé", "vehicle_model": "Honda CR-V", "vehicle_year": 2008,
        "problem_description": "Le démarreur est difficile, surtout quand il fait humide le matin.",
        "cause": "L'humidité saline de Limbé corrode les connexions électriques du démarreur et du circuit d'allumage. Les contacts s'oxydent plus rapidement qu'à l'intérieur du pays.",
        "solution": "Nettoyez et protégez toutes les connexions électriques avec un spray anti-humidité. Vérifiez les bougies et le câblage. Remplacez le démarreur si nécessaire.",
    },
    {
        "name": "Ange", "city": "Limbé", "vehicle_model": "Suzuki Vitara", "vehicle_year": 2006,
        "problem_description": "Les amortisseurs claquent sur la route entre Limbé et Buea, très cabossée.",
        "cause": "La route Limbé-Buea est l'une des plus dégradées de la région. Les chocs répétés mettent rapidement les amortisseurs en fin de vie.",
        "solution": "Remplacez les amortisseurs par des modèles renforcés à gaz. Contrôlez aussi les silentblocs et les rotules.",
    },
    {
        "name": "Madeleine", "city": "Limbé", "vehicle_model": "Nissan Patrol", "vehicle_year": 2001,
        "problem_description": "Le moteur diesel consomme beaucoup, perte de puissance en montée vers Buea.",
        "cause": "Filtres à air et à carburant encrassés par la poussière volcanique et l'humidité. Les injecteurs diesel sont très sensibles à l'eau dans le carburant.",
        "solution": "Remplacez les filtres à air, à carburant et à huile. Faites purger le filtre à eau du circuit diesel. Faites vérifier les injecteurs par un spécialiste.",
    },
    {
        "name": "Pierre", "city": "Limbé", "vehicle_model": "Toyota Prado", "vehicle_year": 2012,
        "problem_description": "Les phares s'allument parfois seuls, des problèmes électriques bizarres et aléatoires.",
        "cause": "L'humidité saline de Limbé infiltre les boîtiers électroniques et les connecteurs. Les courts-circuits dus à l'oxydation provoquent des comportements aléatoires.",
        "solution": "Faites un diagnostic électronique complet. Protégez les connecteurs avec de la graisse diélectrique. Vérifiez les masses électriques, souvent corrodées en zone côtière.",
    },

    # ═══════════════ BUEA ═══════════════
    {
        "name": "Samuel", "city": "Buea", "vehicle_model": "Toyota Corolla", "vehicle_year": 2013,
        "problem_description": "Les freins chauffent et perdent de l'efficacité dans les longues descentes vers Limbé.",
        "cause": "Les descentes abruptes des flancs du mont Cameroun provoquent une surchauffe des freins (fading). L'usage excessif en descente évapore le liquide de frein.",
        "solution": "En descente, utilisez le frein moteur (rétrograder) plutôt que les freins seuls. Vérifiez le niveau et l'état du liquide de frein. Contrôlez les disques et tambours.",
    },
    {
        "name": "Grace", "city": "Buea", "vehicle_model": "Nissan X-Trail", "vehicle_year": 2011,
        "problem_description": "Le véhicule glisse et perd la traction sur les routes mouillées et boueuses de Buea.",
        "cause": "Les routes de Buea, souvent humides et boueuses à cause des fortes pluies et du brouillard du mont Cameroun, usent rapidement les pneus. Une bande de roulement insuffisante est très dangereuse.",
        "solution": "Vérifiez la profondeur des sculptures des pneus (minimum 3mm recommandé). Remplacez les pneus lisses. Pour Buea, privilégiez des pneus tout-terrain ou mixtes.",
    },
    {
        "name": "Emmanuel", "city": "Buea", "vehicle_model": "Toyota Hilux", "vehicle_year": 2009,
        "problem_description": "La boîte de vitesses craque et passe mal les rapports, surtout en montée.",
        "cause": "Les montées à forte pente de Buea sollicitent extrêmement la boîte de vitesses. Un niveau d'huile de boîte insuffisant ou dégradé accélère l'usure des synchroniseurs.",
        "solution": "Vérifiez et changez l'huile de boîte de vitesses. Si les symptômes persistent, faites diagnostiquer par un spécialiste. Agissez tôt — la réparation d'une boîte est coûteuse.",
    },
    {
        "name": "Delphine", "city": "Buea", "vehicle_model": "Mitsubishi L200", "vehicle_year": 2007,
        "problem_description": "Les essuie-glaces ne suffisent plus par temps de brouillard intense, la visibilité est très réduite.",
        "cause": "Le brouillard dense et les pluies abondantes de Buea usent rapidement les balais d'essuie-glace.",
        "solution": "Remplacez les balais d'essuie-glace tous les 6 mois dans les zones humides. Appliquez un traitement hydrophobe sur le pare-brise. Vérifiez que le lave-glace est plein.",
    },
    {
        "name": "Bertrand", "city": "Buea", "vehicle_model": "Land Rover Defender", "vehicle_year": 2005,
        "problem_description": "Le 4x4 dysfonctionne, le véhicule ne passe plus en mode 4 roues motrices.",
        "cause": "L'humidité et la boue pénètrent dans le boîtier de transfert et les cardans. Les joints de cardan sont souvent endommagés sur les pistes boueuses des flancs du mont Cameroun.",
        "solution": "Vérifiez les soufflets de cardan. Faites vidanger et nettoyer le boîtier de transfert. Inspectez régulièrement le dessous de caisse.",
    },

    # ═══════════════ BAFOUSSAM ═══════════════
    {
        "name": "Thérèse", "city": "Bafoussam", "vehicle_model": "Toyota Hilux", "vehicle_year": 2008,
        "problem_description": "La suspension avant est très abîmée, bruits métalliques permanents sur la route Douala-Bafoussam.",
        "cause": "L'axe Douala-Bafoussam est l'un des plus accidentogènes du pays. Les chocs répétés sur les nids-de-poule détruisent les amortisseurs, biellettes et rotules.",
        "solution": "Inspection complète de la suspension. Pour cet axe, optez pour des amortisseurs renforcés à gaz (80 000 FCFA l'unité).",
    },
    {
        "name": "Laurent", "city": "Bafoussam", "vehicle_model": "Renault Duster", "vehicle_year": 2018,
        "problem_description": "Le turbo siffle et il y a moins de puissance depuis que je fais souvent la route des champs.",
        "cause": "Les pistes agricoles de la région chargent le filtre à air en poussière de terre rouge. Un filtre colmaté prive le turbo d'air et le détériore progressivement.",
        "solution": "Remplacez le filtre à air immédiatement. Inspectez les durites d'admission. Sur pistes en terre, changez le filtre à air 2x plus souvent qu'ailleurs.",
    },
    {
        "name": "Cécile", "city": "Bafoussam", "vehicle_model": "Mitsubishi Pajero", "vehicle_year": 2004,
        "problem_description": "Le moteur surchauffe dans les longues montées vers Bafoussam depuis Bafang.",
        "cause": "Les longues montées sollicitent fortement le système de refroidissement. À 1400m d'altitude, le point d'ébullition du liquide de refroidissement est légèrement plus bas.",
        "solution": "Vérifiez le radiateur, le thermostat et la pompe à eau. Remplacez le liquide de refroidissement. N'ouvrez jamais un radiateur chaud.",
    },
    {
        "name": "Francis", "city": "Bafoussam", "vehicle_model": "Toyota Prado", "vehicle_year": 2016,
        "problem_description": "Le véhicule tire vers la droite après avoir roulé sur un nid-de-poule important.",
        "cause": "Un choc violent sur un nid-de-poule peut désaligner instantanément les trains roulants. Fréquent sur l'axe Douala-Bafoussam.",
        "solution": "Faites une géométrie complète des trains roulants (parallélisme + carrossage). Vérifiez qu'aucune pièce de suspension n'a été pliée. Équilibrez les roues.",
    },
    {
        "name": "Albert", "city": "Bafoussam", "vehicle_model": "Toyota Land Cruiser", "vehicle_year": 2000,
        "problem_description": "La batterie est à plat toutes les nuits, je dois brancher un chargeur externe.",
        "cause": "Consommation parasite qui vide la batterie. Alternateur défaillant ou batterie en fin de vie, aggravé par les températures froides des nuits en altitude à Bafoussam.",
        "solution": "Mesurez la consommation au repos (ne doit pas dépasser 50mA). Testez l'alternateur. Si la batterie a plus de 3 ans, remplacez-la.",
    },

    # ═══════════════ GAROUA ═══════════════
    {
        "name": "Moussa", "city": "Garoua", "vehicle_model": "Toyota Land Cruiser", "vehicle_year": 2005,
        "problem_description": "Le radiateur fuit et le moteur surchauffe systématiquement, même sur de courts trajets.",
        "cause": "Avec des températures ambiantes de 40°C et plus à Garoua, le système de refroidissement est à rude épreuve en permanence. Les joints de radiateur cèdent rapidement sous la chaleur.",
        "solution": "Remplacez le radiateur ou faites réparer la fuite. Changez le liquide de refroidissement. Vérifiez le thermostat et la pompe à eau.",
    },
    {
        "name": "Adamou", "city": "Garoua", "vehicle_model": "Nissan Patrol", "vehicle_year": 2003,
        "problem_description": "Le filtre à air est complètement bouché par la poussière, le moteur manque d'air et de puissance.",
        "cause": "La poussière sahélienne de Garoua colmate le filtre à air beaucoup plus vite qu'au Sud. Un filtre saturé prive le moteur d'air, réduit les performances et abîme le turbo.",
        "solution": "Changez le filtre à air tous les 5 000 km à Garoua (au lieu des 15 000 km habituels). Vérifiez les durites d'admission. Évitez de rouler derrière des véhicules qui soulèvent la poussière.",
    },
    {
        "name": "Ibrahim", "city": "Garoua", "vehicle_model": "Mitsubishi L200", "vehicle_year": 2010,
        "problem_description": "Les pneus éclatent souvent à cause de la chaleur de la route bitumée surchauffée.",
        "cause": "Le bitume de la RN1 à Garoua peut atteindre 70°C en pleine journée. Cette chaleur extrême ramollit les pneus et provoque des éclatements, surtout les flancs.",
        "solution": "Roulez avec une pression légèrement inférieure à la normale en forte chaleur. Évitez de rouler entre 12h et 16h. Vérifiez l'état des flancs régulièrement.",
    },
    {
        "name": "Fanta", "city": "Garoua", "vehicle_model": "Toyota Corolla", "vehicle_year": 2012,
        "problem_description": "La direction assistée est dure et grince, surtout après une longue pause au soleil.",
        "cause": "La chaleur extrême de Garoua dégrade rapidement l'huile de direction assistée. Les flexibles de direction vieillissent vite sous 40°C+. Le fluide s'évapore partiellement.",
        "solution": "Vérifiez et complétez le niveau d'huile de direction assistée. Si les durites sont fissurées, remplacez-les. Garez toujours à l'ombre.",
    },
    {
        "name": "Daouda", "city": "Garoua", "vehicle_model": "Toyota Hilux", "vehicle_year": 2007,
        "problem_description": "La suspension est complètement détruite après la route Garoua-Maroua sur la NR1.",
        "cause": "La RN1 entre Garoua et Maroua oblige à rouler plus de 4 heures sur 200 km à cause de son état dégradé. Les chocs répétés sur les ornières détruisent amortisseurs, biellettes et rotules.",
        "solution": "Inspection complète de la suspension avant et arrière. Remplacez tous les composants défaillants. Pour cet axe, équipez-vous d'amortisseurs renforcés et roulez lentement.",
    },
    {
        "name": "Hassana", "city": "Garoua", "vehicle_model": "Peugeot 504", "vehicle_year": 1998,
        "problem_description": "La pompe à carburant tombe souvent en panne, la voiture cale sans raison apparente.",
        "cause": "Les fortes chaleurs font monter la température du carburant dans le réservoir, provoquant des bulles de vapeur (vapeur lock) qui bloquent la pompe sur les véhicules anciens.",
        "solution": "Si possible, garez à l'ombre et laissez refroidir. Remplacez la pompe à carburant si défaillante. Sur les vieux modèles, isolez le circuit d'alimentation de la chaleur moteur.",
    },

    # ═══════════════ NGAOUNDÉRÉ ═══════════════
    {
        "name": "Oumarou", "city": "Ngaoundéré", "vehicle_model": "Toyota Land Cruiser", "vehicle_year": 2006,
        "problem_description": "La boîte de vitesses chauffe et patine dans les longues montées de la falaise de Mbé.",
        "cause": "La falaise de Mbé est l'une des montées les plus exigeantes du Cameroun. Le patinage prolongé surchauffe le convertisseur de couple sur les boîtes automatiques.",
        "solution": "Rétrogradez avant les montées plutôt qu'en cours de montée. Changez l'huile de boîte et le fluide ATF. Évitez le patinage prolongé sur les pentes.",
    },
    {
        "name": "Aminatou", "city": "Ngaoundéré", "vehicle_model": "Nissan X-Trail", "vehicle_year": 2014,
        "problem_description": "Le moteur cale par manque de puissance entre Ngaoundéré et Garoua, surtout en altitude.",
        "cause": "À 1100m d'altitude, l'air est moins dense, ce qui peut affecter la combustion des moteurs anciens non turbocompressés. Le carburant de mauvaise qualité aggrave le problème.",
        "solution": "Faites régler la carburation ou la gestion moteur pour l'altitude. Changez les filtres à air et à carburant. Approvisionnez-vous dans les stations reconnues de Ngaoundéré.",
    },
    {
        "name": "Vourra", "city": "Ngaoundéré", "vehicle_model": "Mitsubishi Pajero", "vehicle_year": 2008,
        "problem_description": "Les amortisseurs claquent fort sur la traversée urbaine de Ngaoundéré, la route est très trouée.",
        "cause": "La traversée urbaine de Ngaoundéré est dans un état de dégradation avancée. Les trous béants entre Dang et le centre-ville brisent les amortisseurs.",
        "solution": "Remplacez les amortisseurs défaillants. Vérifiez les silentblocs et rotules. Roulez lentement dans la traversée urbaine et contournez les trous.",
    },
    {
        "name": "Halilou", "city": "Ngaoundéré", "vehicle_model": "Toyota Corolla", "vehicle_year": 2016,
        "problem_description": "La batterie est à plat le matin par temps froid, la voiture ne démarre pas.",
        "cause": "Les nuits fraîches de Ngaoundéré (altitude 1100m) réduisent temporairement la capacité de la batterie. Une batterie vieillissante supporte mal les démarrages à froid.",
        "solution": "Testez la batterie et l'alternateur. Remplacez la batterie si elle a plus de 3 ans. Utilisez un chargeur automatique la nuit en saison froide.",
    },
    {
        "name": "Mariam", "city": "Ngaoundéré", "vehicle_model": "Renault Duster", "vehicle_year": 2019,
        "problem_description": "Les freins à disque grincent au premier freinage le matin à cause de la rosée.",
        "cause": "La rosée nocturne abondante à l'altitude de Ngaoundéré forme une légère couche de rouille sur les disques après une nuit à l'air libre. Elle disparaît après quelques freinages.",
        "solution": "Ce phénomène est normal et sans danger. Faites quelques freinages légers au démarrage. Si le bruit persiste toute la journée, vérifiez l'état des disques et plaquettes.",
    },

    # ═══════════════ MAROUA ═══════════════
    {
        "name": "Bouba", "city": "Maroua", "vehicle_model": "Toyota Land Cruiser", "vehicle_year": 2004,
        "problem_description": "Le moteur surchauffe en permanence, même au ralenti. La ville est une fournaise.",
        "cause": "Maroua est l'une des villes les plus chaudes du Cameroun avec des pics réguliers de 45°C. Ces températures mettent le système de refroidissement à l'épreuve en permanence.",
        "solution": "Vérifiez l'état du radiateur, du thermostat et de la pompe à eau. Changez le liquide de refroidissement (mélange eau-glycol anti-ébullition). Évitez de rouler aux heures les plus chaudes.",
    },
    {
        "name": "Hamidou", "city": "Maroua", "vehicle_model": "Nissan Patrol", "vehicle_year": 2002,
        "problem_description": "Le sable de l'harmattan s'infiltre partout, le filtre à air est noir en quelques jours.",
        "cause": "Les tempêtes de sable venues du Sahara (harmattan) balayent régulièrement Maroua. Le sable pénètre dans tous les systèmes et colmate le filtre à air en quelques jours.",
        "solution": "Changez le filtre à air tous les 3 000 km à Maroua. Nettoyez régulièrement les injecteurs. Pendant les tempêtes de sable, garez à l'abri et couvrez les prises d'air.",
    },
    {
        "name": "Ramatou", "city": "Maroua", "vehicle_model": "Toyota Hilux", "vehicle_year": 2009,
        "problem_description": "Les joints d'huile moteur fuient à cause de la dilatation excessive causée par la chaleur.",
        "cause": "À 45°C ambiants, la dilatation thermique du moteur est extrême. Les joints d'étanchéité vieillissent prématurément et les fuites d'huile sont fréquentes sur les véhicules anciens.",
        "solution": "Remplacez les joints d'huile défaillants. Utilisez une huile moteur à haute viscosité adaptée à la chaleur extrême (20W50 ou 15W50). Vérifiez le niveau toutes les semaines.",
    },
    {
        "name": "Boukar", "city": "Maroua", "vehicle_model": "Peugeot 405", "vehicle_year": 2000,
        "problem_description": "La peinture et les plastiques extérieurs se fissurent et s'écaillent rapidement.",
        "cause": "Les UV intenses du Sahel et les températures extrêmes de Maroua dégradent la peinture et les plastiques en 2-3 ans. Les joints caoutchouc durcissent et se fissurent.",
        "solution": "Appliquez une cire protectrice UV régulièrement. Garez à l'ombre impérativement. Traitez les joints avec un produit revitalisant caoutchouc.",
    },
    {
        "name": "Fadimatou", "city": "Maroua", "vehicle_model": "Mitsubishi Pajero", "vehicle_year": 2007,
        "problem_description": "La route Maroua-Mora est coupée après les pluies, les amortisseurs ont explosé sur les pistes de déviation.",
        "cause": "Les pluies de la courte saison humide rendent les routes de l'Extrême-Nord impraticables. Les pistes de déviation en terre sont devastatrices pour les suspensions.",
        "solution": "Équipez-vous d'amortisseurs renforcés tout-terrain. En saison des pluies, utilisez impérativement le mode 4x4. Emportez toujours un kit de dépannage et une roue de secours.",
    },

    # ═══════════════ EBOLOWA ═══════════════
    {
        "name": "Abeng", "city": "Ebolowa", "vehicle_model": "Toyota Hilux", "vehicle_year": 2006,
        "problem_description": "La voiture dépense plus en réparations qu'en carburant sur les pistes Ebolowa-Akom II, la suspension est HS à chaque voyage.",
        "cause": "Les pistes de la région Sud vers Akom II sont parmi les plus destructrices du pays. Un chauffeur local témoigne dépenser 60 000 à 70 000 FCFA au garage pour chaque voyage aller-retour.",
        "solution": "Inspectez la suspension après chaque voyage Ebolowa-Akom II. Investissez dans des amortisseurs renforcés tout-terrain. Roulez lentement et évitez la surcharge.",
    },
    {
        "name": "Mballa", "city": "Ebolowa", "vehicle_model": "Nissan X-Trail", "vehicle_year": 2013,
        "problem_description": "La carrosserie rouille rapidement à cause de l'humidité permanente de la forêt équatoriale.",
        "cause": "Ebolowa est entourée de forêt équatoriale dense avec une humidité quasi permanente. Cette humidité associée aux températures chaudes crée les conditions idéales pour la corrosion rapide.",
        "solution": "Traitez le dessous de caisse avec un produit anticorrosion chaque année. Lavez régulièrement la boue forestière. Séchez soigneusement les zones humides.",
    },
    {
        "name": "Zogo", "city": "Ebolowa", "vehicle_model": "Toyota Corolla", "vehicle_year": 2011,
        "problem_description": "Le moteur cale souvent dans les flaques et les passages inondés de la route vers Sangmelima.",
        "cause": "La route Ebolowa-Sangmelima est impraticable par temps de pluie. Les passages inondés peuvent provoquer l'aspiration d'eau dans le moteur (coup d'eau), fatal pour le moteur.",
        "solution": "Ne traversez jamais un point d'eau dont vous ne connaissez pas la profondeur. Si de l'eau entre dans le moteur, coupez immédiatement. Faites diagnostiquer avant de redémarrer.",
    },
    {
        "name": "Essono", "city": "Ebolowa", "vehicle_model": "Mitsubishi L200", "vehicle_year": 2008,
        "problem_description": "Les câbles électriques rongés dans le moteur, des problèmes électriques partout.",
        "cause": "L'humidité de la forêt équatoriale favorise la prolifération de rongeurs qui s'abritent sous le capot et rongent les câbles électriques. Problème très fréquent à Ebolowa.",
        "solution": "Inspectez régulièrement le compartiment moteur. Utilisez des répulsifs pour rongeurs. Réparez immédiatement les câbles rongés — un court-circuit peut déclencher un incendie.",
    },
    {
        "name": "Nkolo", "city": "Ebolowa", "vehicle_model": "Toyota RAV4", "vehicle_year": 2015,
        "problem_description": "Les pneus crevés très fréquemment sur les pistes forestières avec des pierres et racines.",
        "cause": "Les pistes forestières d'Ebolowa sont parsemées de pierres, racines affleurantes et ferrailles. Les flancs des pneus sont particulièrement vulnérables.",
        "solution": "Montez des pneus à flancs renforcés (tout-terrain). Roulez lentement sur les pistes. Transportez toujours une roue de secours en bon état, un cric et une clé de roue.",
    },
]


def seed_database():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            name TEXT, city TEXT, vehicle_model TEXT,
            vehicle_year INTEGER, problem_description TEXT,
            cause TEXT, solution TEXT, created_at TEXT
        )
    """)

    base_date = datetime.utcnow()
    inserted = 0

    print("🚀 Insertion des données en cours...\n")
    for report in REPORTS:
        days_ago = random.randint(1, 180)
        created_at = (base_date - timedelta(days=days_ago)).isoformat()
        cur.execute("""
            INSERT INTO reports (name, city, vehicle_model, vehicle_year,
                                 problem_description, cause, solution, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (report["name"], report["city"], report["vehicle_model"], report["vehicle_year"],
              report["problem_description"], report["cause"], report["solution"], created_at))
        inserted += 1
        print(f"  ✅ [{report['city']:<14}] {report['name']:<12} — {report['vehicle_model']} {report['vehicle_year']}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✅ {inserted} signalements insérés avec succès !\n")
    print("📊 Répartition par ville :")
    for city, count in sorted(Counter(r["city"] for r in REPORTS).items()):
        print(f"  {city:<14} {'█' * count} ({count})")


if __name__ == "__main__":
    if not DATABASE_URL:
        print("❌ Erreur : DATABASE_URL n'est pas définie.")
        print("   Exportez-la : export DATABASE_URL='postgresql://...'")
        exit(1)
    seed_database()
