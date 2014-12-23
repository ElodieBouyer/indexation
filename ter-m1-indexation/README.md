# Module d'indexation et de recherche, utilisant la librairie Xapian


## Installation 

Télécharger la librairie xapian-core sur le site http://xapian.org/download

    $ cd xapian-core-X
    $ ./configure
    $ make
    $ sudo make install

PHP-5 est aussi nécessaire :

    $ sudo apt-get install php5-dev php5-cli

Pour la désindexation, vous aurez besoin de mysql pour python :

    $ sudo apt-get install python-mysqldb


## Indexation

### Configuration

Pour configurer ce module, il faut créer un fichier 'conf.ini' dans le dossier 'indexation-module' (le dossier contenant les scripts d'indexations).

Ce sript doit avoir la forme :

    [xapian]
    database = /home/elodie/Documents/master-1/cours-S2/ter/database/
    pdf = /home/elodie/Documents/master-1/cours-S2/ter/pdfs/

    [database]
    DB_HOST = localhost
    DB_USER = root
    DB_PWD  = 
    DB_NAME = projet_ter
   

Le chemin à donner est le chemin menant à la base de données Xapian.

### Exemple

#### Exemple de code Python pour indexer un fichier :

    import indexationXapian

    # Initialise l'indexation.
    ind = indexationXapian.IndexationXapian()

    # Indexe un pdf.
    # Le premier parametre est le chemin reel du fichier,
    # Le second et le chemin que l'on veut garder dans la base de donnees.
    pid = ind.index("/home/elodie/Documents/master-1/cours-S2/ter/indexation-module/boamp/abcd1285-809a-46a0-94a2-8cd79ea297c6.pdf", "boamp/abcd1285-809a-46a0-94a2-8cd79ea297c6.pdf")

    # Affiche l'identidiant du pdf indexe.
    print pid 


#### Exemple de code python pour indexer plusieurs fichier en même temps :

    import indexationXapian

    # Initialise l'indexation.
    ind = indexationXapian.IndexationXapian()
    
    """ 
    On passe en paramètre :
       - Le chemin vers le dossier contenant les pdf.
       - Une liste de nom de pdf.
    La fonction retourne un dictionnaire pid/nom_pdf.
    """
    pid = ind.indexAll("/home/elodie/Documents/master-1/cours-S2/ter/TerPdf/",
					["boamp/b2fd88fd-3ee0-4a6a-af67-f3cf3401ce2a.pdf",
					 "boamp/b1b10437-04f0-4062-8231-82c0170c66f7.pdf",
					 "boamp/b0177496-f494-4925-9169-6fdae190cb2c.pdf"])


#### Exemple pour désindexer un fichier :

    import indexationXapian

    # Initialise l'indexation.
    ind = indexationXapian.IndexationXapian()

    # Pour desindexer un fichier.
    ind.deindexOnePdf(pid)


#### Exemple pour désindexer tous les vieux avis :

    import old_avis

    oldavis = old_avis.OldAvis()
    oldavis.deindexOldAvis()
    
    
#### Exemple pour indexer tous les nouveaux avis inserés en base.
    import indexationXapian
    import index_all_avis
    

    indexAll = index_all_avis.IndexAll()
    indexAll.indexAllAvis()


## Recherche

### Configuration

Pour configurer ce module, il faut créer un fichier 'conf.ini' dans le dossier 'search-module' (le dossier contenant les scripts d'indexations).

Ce sript doit avoir la forme :

    [xapian]
    xapianDatabase = /home/elodie/Documents/master-1/cours-S2/ter/database/
    xapianSearch   = /home/elodie/Documents/master-1/cours-S2/ter/search-module/

Le chemin à donner est le chemin menant à la base de données Xapian.

### Exemple

Exemple de code php pour effectuer une recherche et avoir des résultats :


    <?php 
    
        include "ExecSearchXapian.php";

        # Lance la recherche avec le script python, la base de donnée et les mot de la recherche.
        $_execSearch = new ExecSearchXapian();

        # Donne la liste des résultats pour le terme "Autres".
        # On veut 2 résultats, et cela concerne la première page.
        $_result = $_execSearch->GetResult("Autres", "1", "10");
        
        # Pour avoir le nombre de résultat total.
        print "Nombre de résultat = ".$_execSearch->GetNbResultat();
    
        # Pour avoir la liste des suggestions (s'il y en a).
        print "Suggestions = ".$_execSearch->GetSuggestions();

        # Pour chaque résultat, affiche le détail.
        for ($i=0 ; $i <= count($_result->GetAllAvis())-1 ; $i++) {
            $percent = $_result->GetAllAvis()[$i]->Percent();
            $url     = $_result->GetAllAvis()[$i]->Url();
            $resume  = $_result->GetAllAvis()[$i]->Resume();

            print "Avis $i : \n";
            print "   Percent = $percent \n";
            print "   URL= $url \n";
            print "   Resume= $resume \n";
        }

    ?>
