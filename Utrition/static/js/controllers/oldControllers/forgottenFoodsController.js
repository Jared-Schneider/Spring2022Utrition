'use strict';

app.controller('ForgottenFoodsCtrl', ['$scope', 'foodService', function($scope, foodService) {

    var categories  = ["Cereals, Breads, Snacks",
        "Meat, Fish, Eggs",
        "Spaghetti, Mixed Dishes, Soups",
        "Dairy Products",
        "Vegetables and Grains",
        "Sauces and Condiments",
        "Fruits",
        "Sweets",
        "Beverages and Alcohol"];
    var counter = 0;
    $scope.done = false;
    update();
    reset();
    $scope.meals = foodService.getMeals();

    $scope.next = function(){
        if (counter < categories.length - 1){
            counter++;
        }
        update();
    };
    $scope.previous = function(){
        if (counter > 0){
            counter--;
        }
        update();
    };
    $scope.addFood = function(foodName, mealName){
        if(foodName){
            foodService.addFood(foodName, mealName)
        }
        reset();
    };
    $scope.remove = function(index){
        foodService.deleteFood(index);
        reset();
    };
    function update(){
        $scope.currentCategory = categories[counter];
        if (counter == categories.length -1){
            $scope.done = true;
            var doMeals = foodService.hasUndeclaredMeals();
            $scope.nextLink = doMeals ? '#/meal' : '#/time';
            angular.element('#nextPage').focus();
        }else{
            $scope.done = false;
            $scope.nextLink = '';
        }
    }
    function reset(){
        $scope.food = '';
        $scope.meal = '';
        angular.element('#nextCategory').focus();
    }
}]);
