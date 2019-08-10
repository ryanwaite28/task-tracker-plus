'use strict';

App.controller("signin-ctrl", ["$scope", function($scope){

  $scope.sign_up = function() {
    let obj = {
      email: $scope.email_input && $scope.email_input.trim() || '',
      password: $scope.password_input && $scope.password_input.trim() || ''
    };
    utils.disable_action_items();
    client.send_request("/sign_in", "PUT", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      setTimeout(function(){ window.location.href = '/home' }, 1000);
    })
  }

}]);
