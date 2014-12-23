# Module de scraping utilisant scrapy

## Installation 

Tous les paquets sont disponibles dans les dépots officiels (testé sous débian stable). 

```
# apt-get install python python-dev python-pip python-lxml python-mysqldb libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info xvfb
#pip install scrapy
#pip install beautifulsoup4
#pip install pisa
#pip install html5lib
```

## Configuration

Renommez le fichier settings.py.sample en settings.py.
Changez les valeurs de connexions à la base de données ainsi que l'emplacement où seront situés les PDFs.

Dans ce fichier on retrouve les configurations de base des scrapers. Changer une configuration dans ce fichier impactera tous les scrapers qui ne surchargent pas le paramètre.

## Lancer un scraper

Les scrapers se lancent indépendament les uns des autres et se lancent en ligne de commande :

```
scrapy crawl [spiderName]
```
Cette ligne de commande doit être lancée depuis le répertoire contenant le projet. Pour cela pensez à faire un "cd" avant (valable aussi pour les crons).

Par exemple pour lancer le scraper du boamp il faut executer la commande "scrapy crawl boamp".
Il est aussi possible de lancer les scraper sur une date antérieure en ajoutant les paramètres suivants :
-a day=X
-a month=Y
-a year=Z
En sachant que les trois peuvent être mis en même temps pour faire une date complète en veillant à mettre le "-a" devant chacun des trois arguments.

## Passage régulier des crawlers

Les crawlers peuvent passer à intervalle régulier. Pour cela des crons peuvent être configurés pour chacun des crawlers.
D'autres alternativement peuvent être envisagées comme la création d'un daemon qui lancera les crawlers les uns après les autres ou en parallèle, etc. Tous les langages peuvent être utilisés temps qu'ils peuvent executer des lignes de commandes.