var app = angular.module('Hackathon', ['ngRoute']);
app.config(function($routeProvider) {
    $routeProvider
        .when('/products', {
            templateUrl: 'idkDude/products.html',
            controller: 'ProductController'
        })
        .when('/details', {
            templateUrl: 'idkDude/details.html',
            controller: 'DetailsController'
        })
        .otherwise({
            redirectTo: '/products'
        });
});

app.controller('ProductController', function($scope){
    //Controller Here
    $scope.message = "Products";
    console.log("Loaded product controller");
});

app.controller('DetailsController', function($scope){
    //Controller Here
    $scope.message = "Details";
    console.log("Loaded details controller");
});
