<?php 

include "AllAvisXapian.php";

class ExecSearchXapian {
	private $_xapianDataBase; # Path to the xapian database.
	private $_result;		  # Search result.
	private $_pythonScript;
	private $_nbPages;
	private $_suggestion;


	function __construct() {
		$myIniFile = parse_ini_file("conf.ini",TRUE);
		$this->_xapianDataBase = $myIniFile["xapian"]["xapianDatabase"];
		$this->_pythonScript   = $myIniFile["xapian"]["xapianSearch"];
	}

	# Effectue une recherche et retourne les résultats.	
	public function GetResult($search, $page, $nbResult) {

		$_args = "python ".$this->_pythonScript."search.py ".$this->_xapianDataBase." ".$page." ".$nbResult." '".str_replace("'", "''", $search)."'";

		$result = shell_exec($_args);

		# On récupère les suggestions.
		$sug = explode("[separatorSug]", $result);
		$this->_suggestion = $sug[0];

		# On récupère le nombre de page. 
		$nbPage = explode("[separatorNb]", $sug[1]);

		$this->_nbPages = $nbPage[0];
		$avis = $nbPage[1];
		
		$_listeAvis = explode("[separatorAvis]", $avis);
		$this->_result = new AllAvisXapian();

		# On sépare les différents avis.
		for ($i=0 ; $i < count($_listeAvis)-1 ; $i++) {
			$_info = explode("[separatorInfo]", $_listeAvis[$i]);
			$_avis = new AvisXapian($_info[0], $_info[1], $_info[2]);
			$this->_result->AddAvis($_avis);
		}
		return $this->_result;
	}

	public function GetNbResultat() {
		return $this->_nbPages;
	}

	public function GetSuggestions() {
		return $this->_suggestion;
	}
}

?>