'use strict';


// Declare app level module which depends on filters, and services
// Creates the routes for each parietal.
// To create a new partial, follow the format below
var app = angular.module('nutritionApp', [
  'ngRoute',
  'ui.sortable'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/start', {templateUrl: '/static/partials/start.html', controller: 'StartCtrl'});
  $routeProvider.when('/add-food', {templateUrl: '/static/partials/add-food.html', controller: 'AddFoodCtrl'});
  $routeProvider.when('/finish', {templateUrl: '/static/partials/finish.html', controller: 'FinishCtrl'});
  $routeProvider.when('/upload', {templateUrl: '/static/partials/upload.html', controller: 'uploadCtrl'});
  $routeProvider.when('/register', {templateUrl: '/static/partials/register.html', controller: 'RegisterCtrl'});
  $routeProvider.when('/bad', {templateUrl: '/static/partials/bad.html', controller: 'ErrorCtrl'});
  $routeProvider.otherwise({redirectTo: '/start'});
}]);
