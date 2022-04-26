'use strict'

app.controller('uploadCtrl', ['$scope', '$http', 'foodService', function($scope, $http, foodService){
    $scope.submit = function() {
        let inFile = document.getElementById('inputFile');

        // send file to app.py
        if (!(inFile.value === "")){
            $http.put('/upload',inFile.files[0]);
        }
    }

 }]);