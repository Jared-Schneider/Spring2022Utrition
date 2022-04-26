'use strict';

app.controller('QuickListCtrl', ['$scope', 'foodService', function($scope, foodService) {
    $scope.meals = foodService.getMeals();

    $scope.addFood = function(foodName, mealName){
        if(foodName){
            foodService.addFood(foodName, mealName)
        }
        reset();
    };
    $scope.remove = function(foodId){
        foodService.deleteFood(foodId)
    };
    function reset(){
        $scope.food = '';
        angular.element("#food").focus()
    }
}]);
