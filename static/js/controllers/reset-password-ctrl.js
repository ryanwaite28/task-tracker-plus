'use strict';

App.controller("reset-password-ctrl", ["$scope", function($scope){

  $scope.resetRequested = false;
  $scope.requestConfirmed = false;

  $scope.submit_password_reset_request = function() {
    let obj = { email: $scope.email_input }
    utils.disable_action_items();
    client.send_request("/submit_password_reset_request", "POST", obj, null)
    .then(function(resp){
      console.log(resp);
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return }
      $scope.resetRequested = true;
      $scope.$apply();
    })
  }

  $scope.submit_password_reset_code = function() {
    let obj = { code: $scope.code_input }
    utils.disable_action_items();
    client.send_request("/submit_password_reset_code", "PUT", obj, null)
    .then(function(resp){
      console.log(resp);
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return }
      $scope.requestConfirmed = true;
      $scope.$apply();
    })
  }

}]);
