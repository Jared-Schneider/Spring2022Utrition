'use strict';

app.controller('ReviewCtrl', ['$scope', 'foodService', function($scope, foodService) {
    $scope.add = false;
    $scope.meals = foodService.getMeals();
    $scope.submit =function(){
        var id = foodService.addFood($scope.food.name, $scope.meal.name);
        foodService.updateFood(id, 'description', $scope.food.description);
        foodService.updateFood(id, 'quantity', $scope.food.quantity);
        foodService.updateFood(id, 'unit', $scope.food.unit);
    }

}]);
