'use strict';

app.controller('AddFoodCtrl', ['$scope', '$compile', 'foodService', function($scope, $compile, foodService) {
//    everything for the controller is contained inside of here.
//    Use $scope instead of 'this'. eg -- $scope.count = 0 instead of this.count = 0
//    public methods/variables: $scope.test=function() {} / $scope.counter
//    private methods/variables: function test() {} / var counter

//    foodService links to the app.service('foodService') found in ../services.js
//    Its basically the backend part that actually holds all of the data. So no need to pass around a JSON
//    Just making helper methods and stuff in there and call those to get the data in here
    var foodListDiv = document.getElementById('foodList'); // needed in multiple functions
    var reminders = new remindBoxes();

    // !main insertion point for the controller.
    // determines what action is taken and calls the appropriate functions
    $scope.update = function(updateType, args) {
        let returnValue = 0
        // based on the update type, start the appropriate controller method.
        // These addFood() and deleteFood() methods just update the model
        if (updateType === 'add') {$scope.addFood();}
        if (updateType === 'delete') {$scope.deleteFood(args);}
        if (updateType === 'remind' && !(document.getElementById('foodList').innerHTML === "" )) {$scope.showRemind();}
        if (updateType === 'back') {reminders.visibility(false);}
        // With the model changed, finish up by calling updateList() to make the view match the 
        // model
        updateList();
    }

    $scope.showRemind = function() {
        reminders.visibility(true);
    }

    // starts the process to add a new food
    $scope.addFood = function() {
        // have the model add the food to the list
        // Checks if the 'food' bar isn't empty and that if the quantity value is more than 0
            // Technically this is already being checked by input constraints, but this is a final check
        if(document.getElementById('mealSelect').value && document.getElementById('quantity').value > 0)
        {
            foodService.addItem();
            // clear the selection to make adding the next food easier
            document.getElementById('foodType').value = "";
            document.getElementById('quantity').value = "";
        }
    }

    // starts the deletion process
    $scope.deleteFood = function(args) {
        // parse out the meal and internal_id for the food to delete
        let meal = args[0];
        let internal_id = args[1];
        // have the model delete the food item
        foodService.deleteFoodItem(meal, internal_id);
    }

    // Overwrites the existing div in addFood that displays all of the food
    // Just call this after any insert/delete to make sure its updated
    function updateList() {
        foodListDiv.innerHTML = "";
        for (let meal of foodService.getMeals().keys()) {
            createMeal(meal, foodService.getMeals().get(meal));
        }
    }

    // private function for updateList
    function createMeal(key, value) {
        // key is the meal (eg "Breakfast"); value is the array of foodItems for this meal

        // Check to make sure there are foods in the group
        if (value != null && value.length != 0) {
            // create the div for the meal group
            let mealGroup = document.createElement('div');
            mealGroup.className = 'mealGroup';
            mealGroup.id = key;
            let mealGroupHeader = document.createElement('h4');
            mealGroupHeader.className = 'mealGroup-header'
            mealGroupHeader.innerHTML = key;
            mealGroup.appendChild(mealGroupHeader);

            // add each individual food to the meal group
            for (let i = 0; i < value.length; i++) {
                // first create the overall div to hold the food
                let currFood = value[i]; // currFood is of type foodItem
                let newFood = document.createElement('div');
                newFood.className = 'foodItem foodItem-flexbox-container';

                // then add a p element to describe this food
                let foodDesc = currFood.describeFood();
                newFood.appendChild(foodDesc);

                // then add a delete button for the food
                let deleteButton = document.createElement('button');
                deleteButton.className = "btn btn-danger delete-food-button";
                // the following makes it so that clicking the button trigger the update() method above
                // Aside from just giving update the 'delete' argument, we also pass two values in an array
                // These are: 1) the meal group for this food, and 2) the internal_id for this foodItem 
                // These will be used by the deleteFoodItem() method in "the model" (=services.js)                
                deleteButton.onclick = function(){
                    $scope.update('delete', [currFood.group, currFood.internal_id]);
                }
                deleteButton.innerHTML = 'Delete';
                newFood.appendChild(deleteButton);

                //  and finally add the food to the meal group box
                mealGroup.appendChild(newFood);
            }
            foodListDiv.appendChild(mealGroup);
        }
    }
    updateList();
}])

