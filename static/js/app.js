const App = angular.module("App", ["ngResource"]);

App.config(['$interpolateProvider', function($interpolateProvider) {
	$interpolateProvider.startSymbol('((');
	$interpolateProvider.endSymbol('))');
}]);

App.config(['$resourceProvider', function($resourceProvider) {
  // Strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = true;
}]);
