<?php 

include "AvisXapian.php";

# Classe pour stocker les informations sur un seul avis.
class AllAvisXapian {
	private $_allAvis;

	# Constructeur -> construit une liste vide.
	function __construct() {
    	$this->_allAvis = array();
    }

	public function AddAvis($avis) {
		array_push($this->_allAvis, $avis);
	}

	public function GetAllAvis(){
		return $this->_allAvis;	
	}

	
}

?>