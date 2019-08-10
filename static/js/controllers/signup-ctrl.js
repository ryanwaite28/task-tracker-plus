'use strict';

App.controller("signup-ctrl", ["$scope", function($scope){

  $scope.capitalize = function(str) {
    if(!str || str.constructor !== String) { return false }
    let Caps = function(string) {
      let s = string.toLowerCase();
      return s.charAt(0).toUpperCase() + s.slice(1);
    }
    return str.split(' ').map(function(sub){ return Caps(sub); }).join(' ');
  }

  $scope.sign_up = function() {
    let obj = {
      displayname: $scope.displayname_input && $scope.capitalize($scope.displayname_input.trim()) || '',
      email: $scope.email_input && $scope.email_input.trim() || '',
      password: $scope.password_input && $scope.password_input.trim() || '',
      confirmpassword: $scope.confirmpassword_input && $scope.confirmpassword_input.trim() || ''
    };
    utils.disable_action_items();
    client.send_request("/sign_up", "POST", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      setTimeout(function(){ window.location.href = '/home' }, 1000);
    })
  }

}]);
