 
 
### Installer les fichiers pour le serveur
 
    sudo apt-get install apache2 php5 mysql-server libapache2-mod-php5 php5-mysql mysql-server-5.0

### Installer MyCrypt

    sudo apt-get install php5-mcrypt
 
### Installer Composer

    https://getcomposer.org/doc/00-intro.md

### Donner les droits de lecture et d'écriture à l'utilisateur

### Activer le mode rewrite

### Redemarrer le serveur

    /etc/init.d/apache2 start

### Donner tous les droits au dossier storage

    chmod -R 777 laravel2/app/storage

### Creer le fichier laravel2/app/config/settings.php

    <?php

    return array(
        //Chemin vers le module de recherche :
        'xapianSearch' => '/.../ter-m1-indexation/search-module',
        //Chemin vers le dossier contenant les pdf :
        'pdf' => '/.../pdf'
        ); ?>

###Creer le fichier laravel2/app/config/database.php

   <?php

    return array(

	    'fetch' => PDO::FETCH_CLASS,

	    'default' => 'mysql',

	    'connections' => array(

		    'mysql' => array(

			    'read' => array(
				    'host' => '127.0.0.1',
				    ),
			    'write' => array(
				    'host' => '127.0.0.1',
			    ),
			    'driver'    => 'mysql',
			    'host'      => '127.0.0.1',
			    'database'  => 'projet_ter',
			    'username'  => 'root',
			    'password'  => '*****',
			    'charset'   => 'utf8',
			    'collation' => 'utf8_unicode_ci',
			    'prefix'    => '',
		    ),

	    ),

	    'migrations' => 'migrations',

	    'redis' => array(

		    'cluster' => false,

		    'default' => array(
			    'host'     => '127.0.0.1',
			    'port'     => 6379,
			    'database' => 0,
		    ),

	    ),

    );
    ?>
