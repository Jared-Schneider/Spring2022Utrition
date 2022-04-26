'use strict';

app.controller('MealCtrl', ['$scope', 'foodService', function($scope, foodService) {
    $scope.foods = foodService.getFoods();
    $scope.meals = foodService.getMeals();
    $scope.unclassifiedFoods = foodService.getUndeclaredFoods();
    $scope.done = false;
    var current = 0;
    update();
    $scope.next = function(){
        if (current < $scope.unclassifiedFoods.length - 1){
            current++;
        }
        $scope.done = current == $scope.unclassifiedFoods.length-1;
        update();
    };
    $scope.previous = function(){
        if (current > 0){
            current--;
        }
        update();
    };
    $scope.update = function(food, meal){
        console.log('update');
        if (meal.name){
            foodService.updateMeal(food.meal, 'name', meal.name);
        }
        update();
    };

    function update(){
        $scope.food = $scope.unclassifiedFoods[current];
        $scope.meal = "";
        angular.element('#meal').focus();
    }

}]);
