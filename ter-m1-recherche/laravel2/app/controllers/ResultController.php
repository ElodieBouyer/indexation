<?php


class ResultController extends BaseController {


  public function telechargerResult($_idAvis){


    $_avis = Avis::where('id', '=', $_idAvis)->first();
    $_path = Config::get('settings.pdf')."/".$_avis->textName;
    
    if(file_exists($_path)){

      header('Content-type:force-download'); 
      header('Content-Disposition: attachment; filename=' . basename($_path));
      readfile($_path);
      exit;  
    }
    else
      return View::make('pages.unknow', array('_titre'=> "pdf introuvable", '_content'=> "Le Pdf que vous recherchez n'est actuellement plus disponible."));
  }

    /**
     * Show the profile for the given avis.
     */

 	/**
     * Philosophie de la fonction showResult($_page).
     *
     * On demande à xapian de nous trouver les $_nbResult qu'il trouve pour les mots-clefs $_recherche.
     * Ensuite, pour chacun de ces résultats, on va chercher tous les détails des avis trouvés dans la BDD
     * grâce aux noms des pdfs retournés par xapian.
     * On ajoute ces détails à $_oneAvis qu'on stocke eux même dans $_allAvis.
     */

 	/**
     * Retours possibles :
     *
	 * Si $_recherche est vide => page d'erreur.
	 * Si $_allAvis est vide, c'est qu'il n'y a pas de résult pour les mots-clefs $_recherche => page d'erreur.
	 * Sinon, on retourne la page de résultat classique.
     */
  public function showResult($_page)
  {	

    	// Inclusion de la classe de recherche
   include Config::get('settings.xapianSearch')."/ExecSearchXapian.php";

    	//Tableau des avis.
   $_allAvis = array();

    	//Etat des boutons "retour" et "suivant" dans la vue associée.
   $_navigation = array();

      //Sauvegarde du Et/Ou choisi.
   $_isSelect = array();

    	//Nombre de résultat voulu à chaque page.
   $_nbResult = 10;

    	//Récupération des mots-clefs
   $_recherche = Input::get('recherche');
   $_searchType = Input::get('searchType');


   $_recherche = rtrim(ltrim(preg_replace('/\s{2,}/', ' ', $_recherche)));

   if ($_searchType == "et"){
    $_recherche2 = str_replace(" AND "," " , $_recherche);
    $_recherche2 = str_replace(" NOT "," " , $_recherche2);
    $_recherche2 = str_replace(" ", " AND ", $_recherche2);
    $_recherche2 = str_replace("AND -"," NOT " , $_recherche2);
    $_isSelect["ET"] = "style=" . '"' . "background: #999999". '"';
    $_isSelect["OU"] = "";

  }

  else {
    $_recherche2 = str_replace(" NOT "," " , $_recherche);
    $_recherche2 = str_replace(" -"," NOT " , $_recherche2);
    $_isSelect["ET"] = "";
    $_isSelect["OU"] = "style=" . '"' . "background: #999999". '"';
  }

  if(!empty($_recherche2)){
      	//Recherche de résultat avec xapian
   $_execSearch = new ExecSearchXapian();
   $_result = $_execSearch->GetResult($_recherche2, $_page, $_nbResult);
   $_nbResultTotal = $_execSearch->GetNbResultat();
   $_suggestion2 = str_replace(" AND ", " ", $_execSearch->GetSuggestions());
   $_suggestion = str_replace(" NOT ", " ", $_suggestion2);

   if ($_suggestion == $_recherche){
    $_suggestion = NULL;
   }

      	// Mise en forme des avis trouvés
   for ($i=0 ; $i <= count($_result->GetAllAvis())-1 ; $i++) {
     $percent = $_result->GetAllAvis()[$i]->Percent();
     $url     = $_result->GetAllAvis()[$i]->Url();
     $resume  = $_result->GetAllAvis()[$i]->Resume();

     $_nomPdf = str_replace("data/", "", $url);
     $_nomPdf = str_replace(" ", "", $_nomPdf);

     $_oneAvis = Avis::where("textName", '=', $_nomPdf)->first();

     $_oneAvis['cpv'] = CPV::where('id_avis', '=', $_oneAvis->id)->get();
     $_oneAvis['url'] = Urls::where('id_avis', '=', $_oneAvis->id)->get();

        	// Dans le cas exceptionnel ou le pdf indexé n'est pas dans la BDD.
     if(empty($_oneAvis)){
       continue;
     } 

     $_oneAvis['resume'] = $resume;
     $_oneAvis['percent'] = $percent;

        	// Ajout de l'avis courant aux autres avis.
     $_allAvis[] = $_oneAvis;

        	// RaZ du tableau de l'avis courant.
     $_oneAvis = array();
   }




        // On va chercher les résultats de la page suivant pour vérifier qu'il y a une page suivante.
 $_result2 = $_execSearch->GetResult($_recherche2, $_page+1, $_nbResult);

      // Si on est sur la première page, il n'y a pas de bouton "précédent".
 if($_page==1){
  $_navigation['previous'] = "disabled";
}
else {
  $_navigation['previous'] = "";
}

      // Si la page suivante n'a pas de résultat, il n'y a pas de bouton "suivant"
if( count($_result2->GetAllAvis()) == 0){
  $_navigation['next'] = "disabled";
}
else {
  $_navigation['next'] = "";
}
 }


if(empty($_recherche)){
  return View::make('pages.unknow', array('_titre'=> "Aucune donnée saisie", '_content'=> "Veuillez saisir des mots-clefs avant de lancer la recherche !"));
}

if(empty($_allAvis)){
  return View::make('pages.unknow', array('_titre'=> "Aucun résultat", '_suggestion' => $_suggestion, '_content'=> "Aucun élément existant avec comme contenu \"".$_recherche."\"  !"));
}
else {
 return View::make('pages.result', array('_allAvis' => $_allAvis, '_suggestion' => $_suggestion,'_currentPage' => $_page, '_recherche' => $_recherche, '_navigation' => $_navigation, '_searchType' => $_searchType, '_nbResultTotal' => $_nbResultTotal, '_isSelect' => $_isSelect ));
}

}


public function showOnlySearchResult()
{ 

  $tutoAccueil = array();
  $tutoAccueil[0] = "Pour effectuer une recherche comportant tous les mots saisies, appuyez sur 'ET'";
  $tutoAccueil[1] = "Pour effectuer une recherche comportant au moins un des mots saisies, appuyez sur 'OU'";
  $tutoAccueil[3] = "Pour effectuer une recherche en excluant un mot, mettez un '-' devant";


  return View::make('pages.unknow', array('_titre'=> "Accueil",'tutoAccueil' => $tutoAccueil, '_content'=> "Veuillez saisir des mots-clefs pour commencer la recherche."));
}

}



