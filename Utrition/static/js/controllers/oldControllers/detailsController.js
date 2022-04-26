'use strict';

app.controller('DetailsCtrl', ['$scope', 'foodService', function($scope, foodService) {
    $scope.meals = foodService.getMeals();
    $scope.done = false;
    let mealIdx = 0;
    let foodIdx = 0;
    function update(){
        $scope.meal = $scope.meals[mealIdx];
        $scope.food = $scope.meal.foods[foodIdx];
    }
    update();

    $scope.next = function(){
        if (foodIdx < $scope.meal.foods.length -1){
            foodIdx++;
        } else{
            foodIdx = 0;
            mealIdx++;
            if (mealIdx > $scope.meals.length -1){
                $scope.done=true;
                return
            }
        }
        update();
    };
    $scope.previous = function(){
        if (foodIdx == 0 ){
            if (mealIdx > 0){
                mealIdx--;
                foodIdx = $scope.meals[mealIdx].foods.length -1;
            }
        } else{
            foodIdx--;
        }
        update();
    };
    $scope.update = function(food){
    }

}]);
