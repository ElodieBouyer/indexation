<!doctype html>
<html>
	<head>
		@include('includes.head')
	</head>

	<body>
		<div class="container">

			<header class="row">
				@include('includes.header')
			</header>

			<div id="main" class="row">
				@section('content-navbar')
				@show

				@section('content')
				@show

				{{--@section('content-navbar')
				@show --}}

			</div>

			<footer class="row">
				@include('includes.footer')
			</footer>

		</div>
	</body>
</html>