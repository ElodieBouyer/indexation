<?php
/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It's a breeze. Simply tell Laravel the URIs it should respond to
| and give it the Closure to execute when that URI is requested.
|
*/

Route::match(array('GET', 'POST'),'result/{page}','ResultController@showResult');
Route::get('telecharger/{idPdf}', 'ResultController@telechargerResult');
Route::get('result', 'ResultController@showOnlySearchResult');
Route::get('/','ResultController@showOnlySearchResult');

App::missing(function($exception)
{
	return View::make('pages.result');
});
?>