'use strict';

/* Directives */

// -------- No idea what this does and if it is even needed anymore now that partials are reworked

app.directive('foodList', function(){
  return {
    controller: function($scope){
      $scope.sortableOptions = {
        connectWith: ".food"
      }
    },
    templateUrl: 'static/templates/food-list-template.html'
  }
})
