<?php 

# Classe pour stocker les informations sur un seul avis.
class AvisXapian  {
	private $_percent;
	private $_url;
	private $_resume;

	function __construct($percent, $url, $resume) {
    	$this->_percent = $percent;
    	$this->_url     = $url;
    	$this->_resume  = $resume;
    }

    public function Percent() {
    	return $this->_percent;
    }

    public function Url() {
    	return $this->_url;
    }

    public function Resume() {
    	return $this->_resume;
    }
}

?>