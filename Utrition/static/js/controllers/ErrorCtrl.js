'use strict'

app.controller('ErrorCtrl', ['$scope', '$http', 'foodService', function($scope, $http, foodService){
  // Gets error information to display on error page 
  $http({
        method: 'PUT',
        url: '/bad',
      }).success(function(data, status){
        $scope.e = data['e']
        $scope.nextPage = data['nextPage']
        $scope.nextURL="3; URL="+data['nextURL']
        $scope.status = status;
        $scope.success = true;
      }).error(function(data, status){
        $scope.e = 'error';
        $scope.status = status;
        $scope.loadURL = data['nextURL']
        $scope.nextPage = data['nextPage']
        $scope.success = false;
      });
 }]);