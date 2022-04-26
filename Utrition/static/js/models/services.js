'use strict';

/* Services */

/*
From what i understand, a service acts much like a model but for angular. Thinking of using this to hold the food
items the customer has created thus far. Would make it very easy to get the data to each of the partial. just need to
pass a reference to this. Its a singleton so it should persist between switching.Similar to how $scope is
passed in addFoodController
*/

app.service('foodService', function() {
    var mealGroups = ['Breakfast','Lunch','Dinner','Snack'];
    var map = new Map(); // Map<string,array(foodItem)>
    var email;


    // weird syntax requires it be wrapped in a return and a ',' separates each function
    return {
        // Triggered when the addFood button is clicked
        addItem:function() {
            // Create a new foodItem object
            let group = document.getElementById('mealSelect').value;
            let item = document.getElementById('foodType').value;
            let quantity = document.getElementById('quantity').value;
            let unit = document.getElementById('unitSelect').value;
            let food_id = document.getElementById("DB_food_id").value
            let food = new foodItem(group,item,quantity,unit,food_id);

            // Add the foodItem to the map
            if (map.has(group)) {
                // There is already items in this group.
                // Push the new item
                let currentFood = map.get(group);
                currentFood.push(food);
                map.set(group,currentFood);
            }
            else {
                // This meal does not have any food
                // Create a new key = group
                // push the new item
                map.set(group,[food]);

            }

        },

        // Deletes the food with the given internal_id from the given meal
        // Eg, deleteFoodItem("Breakfast", 3) deletes the food item in the Breakfast group that has internal_id = 3
        // Triggered when a delete button for a food is clicked
        deleteFoodItem:function(meal, internal_id) {
          let foodItemsArr = map.get(meal); // gets the array of food items for this meal
          for (let i = 0; i < foodItemsArr.length; i++){
            // linearly scan the food items in the array until we find the one with matching internal_id
            let foodItem = foodItemsArr[i];
            if (foodItem.internal_id == internal_id){
              // then once we have that food item, delete it from the array
              foodItemsArr.splice(i, 1);
              break;
            }
          }
          
        },

        // --- Getters ---
        getMeals:function() {
            return map;
        },

        // --- Setters ---
        setEmail:function(newEmail) {
            email = newEmail;
        }
    };

});