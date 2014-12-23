@extends('layouts.default')


@section('content')

<div class="rectangle">
</div>

@foreach($_allAvis as $_avisKey => $_avisValue)
<div id="container" class="row-fluid col-md-12 orange">
  <div class="panel-heading">
    <h3 class="panel-title grey-font">Pertinance  {{$_avisValue->percent}}</h3>
  </div> 

  <div class="row-fluid col-md-6 panel orange">

  {{-- Première ligne --}}
  <table class="table table-bordered table-condensed white">
    <tr>
      <td>
        Type de procedure : {{ $_avisValue['procedureType'] }}
      </td>
      <td> 
        @if (!empty($_avisValue->endDate))
         Remise des plis : {{  date("d/m/Y",strtotime($_avisValue->endDate)) }} 
         @if (intval(date("G",strtotime($_avisValue->endDate))) != 0) {{  date(" à G\hi",strtotime($_avisValue->endDate)) }} @endif
         @else
         Remise des plis : Inconnue
        @endif
      </td>
    </tr>
    <tr>
      <td>
        @if (!empty($_avisValue->reference))
        Référence : {{ $_avisValue->reference }}
        @else
        Référence : Inconnue
        @endif
      </td>
      <td>
      @if (!empty($_avisValue->publicationDate))
      Publié le : {{ date("d/m/Y",strtotime($_avisValue->publicationDate)) }} 
      @if (intval(date("G",strtotime($_avisValue->publicationDate))) != 0) {{  date(" à G\hi",strtotime($_avisValue->publicationDate)) }} @endif
      @endif
      </td>
    </tr>

    <tr>
      <td> 

      @if (!empty($_avisValue->buyingEntity))
      Entité acheteuse : {{ $_avisValue->buyingEntity }}
      @else
      Entité acheteuse : Inconnue
      @endif 
      </td>
      <td>
      @if (!empty($_avisValue->executionPlace) or !empty($_avisValue->departement))
      Lieu d'exécution 
      @if (!empty($_avisValue->departement)) ({{ str_replace(';', ' ;', $_avisValue->departement)}}) @endif
      @if (!empty($_avisValue->executionPlace)) : {{ $_avisValue->executionPlace}} @endif

      @endif
      </td>
    </tr>

    <tr>
      <td>
      @if($_avisValue->numberOfBatch > 0)
      Lot : {{ $_avisValue->numberOfBatch }}
      @else
      Lot : Inconnu
      @endif
      </td>
       <td>
      @if (!empty($_avisValue->cpv))  
      CPV :
      @foreach($_avisValue->cpv as $key => $value)
      {{$value->number}},

      @endforeach

      @endif
      </td>
    </tr>
  </table>
  
</div>



<div class="row-fluid col-md-6 orange">
  <li class="list-group-item"> {{ $_avisValue['object'] }} </li>

  @foreach($_avisValue->url as $key => $value)
  <li class="list-group-item">Url : <a href= {{ $value->url }}> {{ $value->url }} </a></li>
  @endforeach

  <li class="list-group-item"> <a href= {{URL::to('telecharger/'.$_avisValue->id)}} title="Pdf">Télécharger l'avis (.pdf)</a> </li>

</div>
</div>

@endforeach

@stop

@section('content-navbar')

<nav class="navbar navbar-default" role="navigation" orange	id="resultNavbar">

	<form class="navbar-form navbar-left" action={{URL::to('result')}}>
   <button class="btn btn-default" > Accueil </button>
 </form>

 <form class="navbar-form navbar-left" role="search" action={{URL::to('result/1')}} method="post">
  <div class="form-group">
    <input name="recherche" id="wordSearch" value=  {{'"'.$_recherche.'"'}}  type="text" class="form-control" placeholder="Search">
  </div>
  <button type="submit" id="andSearch" name="searchType" title="Résultat comportant tous les mots." value="et" class="btn btn-default" {{$_isSelect['ET']}} >ET</button>
  <button type="submit" id="orSearch" name="searchType" title="Résultat comportant au moins un des mots." value="ou" class="btn btn-default" {{$_isSelect['OU']}}>OU</button>
</form>

<form class="navbar-form navbar-left" action={{URL::to('result/'.($_currentPage-1))}} method="post">
 <input style="display: none;" name="searchType" value=  {{$_searchType}}>
 <button type="submit" class="btn btn-default" name="recherche" value={{'"'.$_recherche.'"'}} {{$_navigation['previous']}}> Précédent</button>
</form>

<form class="navbar-form navbar-left" action={{URL::to('result/'.($_currentPage+1))}} method="post">
 <input type="hidden" name="searchType" value={{$_searchType}}>
 <button type="submit" class="btn btn-default" name="recherche" value={{'"'.$_recherche.'"'}} {{$_navigation['next']}}>Suivant</button>
</form>

<form class="navbar-form navbar-left">
  Page : 
  <input type="text" id="pageSearch" size="2" value={{$_currentPage}} onkeypress="if(event.keyCode < 48 || event.keyCode > 57) event.returnValue = false;" onkeydown="if (event.keyCode == 13){ goAtPage(); return false;}"/>
  / {{ceil($_nbResultTotal/10)}} ({{$_nbResultTotal}} résultat(s) estimé(s))
</form>


</nav>


<form id="suggestionSend" action={{URL::to('result/1')}}>
<input type="hidden" name="recherche" value={{'"'.$_suggestion.'"'}}/>
</form>
<span class="suggestion">
Suggestion : <a href='#'  style="color:#FFF" onclick='document.getElementById("suggestionSend").submit()'>{{$_suggestion}}</a>
</span>

<script>

  function goAtPage(){

    var page = document.getElementById('pageSearch').value;
      if(page > {{ceil($_nbResultTotal/10)}} ){
        page = {{ceil($_nbResultTotal/10)}};
      }
      if(page < 1 ){
        page = 1;
      }
      var recherche = document.getElementById('wordSearch').value;
      var url = "{{URL::to('result')}}";
      url = url + "/" + page;

      if (document.getElementById('andSearch').style.background){
        var operatorChoose ="et";
      }
      else{
        var operatorChoose ="ou";
      }
      console.log(url);
      form = document.createElement('form');
      form.setAttribute('method', 'POST');
      form.setAttribute('action', url);

      myvar = document.createElement('input');
      myvar.setAttribute('name', 'recherche');
      myvar.setAttribute('value', recherche);

      form.appendChild(myvar);

      myvar2 = document.createElement('input');
      myvar2.setAttribute('name', 'searchType');
      myvar2.setAttribute('value', operatorChoose);

      form.appendChild(myvar2);


        //document.body.appendChild(form);
        form.submit();   
 
    }


  </script>

  @stop

