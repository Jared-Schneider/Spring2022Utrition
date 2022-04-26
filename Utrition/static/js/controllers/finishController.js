'use strict';

app.controller('FinishCtrl', ['$scope', '$http', 'foodService', function($scope, $http, foodService){
  
  // Sends food recall info to app.py
  $http({
    method: 'PUT',
    url: '/submit',
    data: Object.fromEntries(foodService.getMeals())
  }).success(function(data){
    $scope.success = true;
  }).error(function(data){
    $scope.success = false;
  });

  // Adding the review foods to the top of the page
  var foodListDiv = document.getElementById('foodList');
  $scope.addMeal = function(meal,foods) {
     if (foods != null && foods.length != 0) {
            // create the div for the meal group
            let mealGroup = document.createElement('div');
            mealGroup.className = 'mealGroup';
            mealGroup.id = meal;
            let mealGroupHeader = document.createElement('h4');
            mealGroupHeader.className = 'mealGroup-header'
            mealGroupHeader.innerHTML = meal;
            mealGroup.appendChild(mealGroupHeader);

            // add each individual food to the meal group
            for (let i = 0; i < foods.length; i++) {
                // first create the overall div to hold the food
                let currFood = foods[i]; // currFood is of type foodItem
                let newFood = document.createElement('div');
                newFood.className = 'foodItem foodItem-flexbox-container';

                // then add a p element to describe this food
                let foodDesc = currFood.describeFood();
                newFood.appendChild(foodDesc);

                //  and finally add the food to the meal group box
                mealGroup.appendChild(newFood);
            }
          foodListDiv.appendChild(mealGroup);
     }
  },

  $scope.createList = function() {
      foodListDiv.innerHTML = "";
      for (let meal of foodService.getMeals().keys()) {
          $scope.addMeal(meal, foodService.getMeals().get(meal));
      }
  }
  $scope.createList();
}]);
