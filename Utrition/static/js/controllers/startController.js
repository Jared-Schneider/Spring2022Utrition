'use strict'

app.controller('StartCtrl', ['$scope', 'foodService', function($scope, foodService){

   $scope.submit = function() {
        foodService.setEmail(document.getElementById('email').value);
   }

 }]);
