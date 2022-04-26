'use strict'

app.controller('RegisterCtrl', ['$scope', '$http', 'foodService', function($scope, $http, foodService){
  // Getting info to display on registration page
  $http({
      method: 'PUT',
      url: '/user',
    }).success(function(data, status){
      $scope.email = data
      $scope.status = status;
      $scope.success = true;
    }).error(function(data, status){
      $scope.email = 'error email';
      $scope.status = status;
      $scope.success = false;
    });
 }]);