@extends('layouts.default')
@section('content')
<div class="rectangle">
</div>

<div  id="container" class="row-fluid">
  <div class="panel orange">
   <div class="panel-heading">
    <h3 class="panel-title"> {{$_titre}}</h3>
   </div>
   <ul class="list-group">
    <li class="list-group-item">
     {{$_content}}
    </li>


    @if (!empty($tutoAccueil))
      @foreach($tutoAccueil as $value)
      <li class="list-group-item">
        {{$value}}
      </li>
      @endforeach
    @endif

   </ul>
  </div>
</div>
@stop

@section('content-navbar')
<nav class="navbar navbar-default" role="navigation" orange id="resultNavbar">

  <form class="navbar-form navbar-left" action={{URL::to('result')}}>
   <button class="btn btn-default" > Accueil </button>
 </form>

 <form class="navbar-form navbar-left" role="search" action={{URL::to('result/1')}} method="post">
  <div class="form-group">
    <input name="recherche" value=""  type="text" class="form-control" placeholder="Search">
  </div>
  <button type="submit" name="searchType" title="Résultat comportant tous les mots." value="et" class="btn btn-default">ET</button>
  <button type="submit" name="searchType" title="Résultat comportant au moins un des mots." value="ou" class="btn btn-default">OU</button>
</form>

<form class="navbar-form navbar-left">
 <button type="submit" class="btn btn-default" name="recherche" value="" disabled> Précédent</button>
</form>

<form class="navbar-form navbar-left">
 <button type="submit" class="btn btn-default" name="recherche" value="" disabled>Suivant</button>
</form>

</nav>

@if (!empty($_suggestion))
<form id="suggestionSend" action={{URL::to('result/1')}}>
  <input type="hidden" name="recherche" value={{'"'.$_suggestion.'"'}}/>
</form>
<span class="suggestion">
  Peut-être vouliez vous chercher :  <a href='#'  style="color:#FFF" onclick='document.getElementById("suggestionSend").submit()'>{{$_suggestion}}</a>
</span>
@endif


@stop