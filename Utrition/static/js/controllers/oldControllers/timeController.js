'use strict';

app.controller('TimeCtrl', ['$scope', 'foodService', function($scope, foodService) {
    $scope.meals = foodService.getMeals();
    $scope.done = false;
    var current = 0;
    update();
    $scope.next = function(){
        if (current < $scope.meals.length - 1){
            current++;
        }
        $scope.done = current == $scope.meals.length - 1;
        update();
    };
    $scope.previous = function(){
        if (current > 0 ){
            current--;
        }
        update();
    };
    $scope.update = function(meal, time){
        console.log("update");
        if(time){
            foodService.updateMeal(meal.id, 'time', time);
        }
        update();
    };
    function update(){
        $scope.meal = $scope.meals[current];
        $scope.mealFoods = _.pluck($scope.meal.foods,  "name");
        $scope.time = "";
        angular.element("#time").focus();
    }

}]);
