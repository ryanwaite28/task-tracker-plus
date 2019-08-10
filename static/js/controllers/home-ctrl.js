'use strict';

App.controller("home-ctrl", ["$scope", function($scope){

  window.scope = function() { 
    console.log($scope); 
  };

  $scope.you = {};
  $scope.tasks = [];

  $scope.tasks_filtered = [];
  $scope.isEditingTask = false;
  $scope.editingTask = null;
  $scope.taskListEnd = false;
  $scope.parentTask = null;
  $scope.isCreatingSubTask = false;
  $scope.filters = utils.filters;
  $scope.currentFilter = $scope.filters.ALL;
  $scope.taskStack = [];

  

  $scope.getTaskFormHeading = function () {
    if ($scope.isEditingTask) {
      return "Edit: " + $scope.editingTask.text;
    }
    if ($scope.isCreatingSubTask) {
      return "Creating subtask for: " + $scope.parentTask.text;
    } 
    return  "Create a Task!";
  };

  $scope.getTaskTestHeading = function () {
    if (!!$scope.taskStack.length) {
      return 'Tasks for: ' + $scope.taskStack[$scope.taskStack.length - 1].text;
    }
    return  "Your tasks";
  };

  $scope.getTaskLengthHeading = function () {
    if (!!$scope.taskStack.length) {
      return $scope.taskStack[$scope.taskStack.length - 1].subtasks.length;
    }
    return  $scope.you.tasks_len;
  };

  $scope.init = function() {
    client.send_request("/check_session", "GET", null, null)
    .then(function(resp){
      $scope.you = resp.user || {};
      return client.send_request("/get_user_tasks", "GET", null, null)
    })
    .then(function(resp){
      $scope.tasks = resp.tasks;
      $scope.tasks_filtered = resp.tasks;
      if($scope.you.tasks_len <= 5) { $scope.taskListEnd = true; }
      $scope.displayname_input = $scope.you.displayname;
      $scope.email_input = $scope.you.email;
      $scope.$apply();
    });
  };

  $scope.init();

  $scope.get_scope_tasks_list = function () {
    const list = !!$scope.taskStack.length ?
      $scope.taskStack[$scope.taskStack.length - 1].subtasks :
      $scope.tasks;

    return list;
  };

  $scope.loadMoreTasks = function() {
    let id_list = $scope.tasks.map(function(t){ return t.id });
    let min_id = id_list.reduce(function(a, b){ return Math.min(a, b) });
    client.send_request("/get_user_tasks/" + min_id, "GET", null, null)
    .then(function(resp){
      if(resp.tasks.length < 5) { $scope.taskListEnd = true; }
      resp.tasks.forEach(function(t){ $scope.tasks.push(t); });
      $scope.apply_tasks_filter();
      $scope.$apply();
    });
  };

  $scope.apply_tasks_filter = function() {
    const list = $scope.get_scope_tasks_list();

    switch($scope.currentFilter) {
      case $scope.filters.ALL:
        $scope.tasks_filtered = [ ...list ];
        return;

      case $scope.filters.DONE:
        $scope.tasks_filtered = list.filter(function(t){ return t.done === true });
        return;

      case $scope.filters.NOT_DONE:
        $scope.tasks_filtered = list.filter(function(t){ return t.done === false });
        return;

      case $scope.filters.LATE:
        $scope.tasks_filtered = list.filter(function(t){ 
          return utils.determine_time_status(t) ===  $scope.filters.LATE;
        });
        return;

      case $scope.filters.DUE_TODAY:
        $scope.tasks_filtered = list.filter(function(t){ 
          return utils.determine_time_status(t) ===  $scope.filters.DUE_TODAY;
        });
        return;

      case $scope.filters.ON_TIME:
        $scope.tasks_filtered = list.filter(function(t){ 
          return utils.determine_time_status(t) ===  $scope.filters.ON_TIME;
        });
        return;

      case $scope.filters.NO_DUE_DATE:
        $scope.tasks_filtered = list.filter(function(t){ 
          return utils.determine_time_status(t) ===  $scope.filters.NO_DUE_DATE;
        });
        return;
    }
  };

  $scope.toggle_editing_account = function() {
    $scope.editingAccount = !$scope.editingAccount;
  };

  $scope.check_account_changes = function() {
    let displaynameChanged = $scope.displayname_input != $scope.you.displayname;
    let emailChanged = $scope.email_input != $scope.you.email;
    return displaynameChanged || emailChanged || false;
  };

  $scope.check_password_changes = function() {
    let passwordChanged = $scope.oldpassword_input && $scope.password_input && $scope.confirmpassword_input;
    return passwordChanged || false;
  };

  $scope.check_edits_changes = function() {
    let textChanged = $scope.taskname_input !== $scope.editingTask.text;
    let duedateChanged = ($scope.taskduedate_input && $scope.taskduedate_input.toJSON() || null) !== ($scope.editingTask.due_date && (new Date($scope.editingTask.due_date)).toJSON() || null);
    return textChanged || duedateChanged || false;
  };

  $scope.check_form = function() {
    let isTextInutValid = !!$scope.taskname_input
    let duedateChanged = ($scope.taskduedate_input && $scope.taskduedate_input.toJSON() || null) !== ($scope.editingTask.due_date && (new Date($scope.editingTask.due_date)).toJSON() || null);
    
    return textChanged || duedateChanged || false;
  };

  $scope.update_account = function() {
    let obj = {
      displayname: $scope.displayname_input,
      email: $scope.email_input
    };
    utils.disable_action_items();
    client.send_request("/update_account", "PUT", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      $scope.you = resp.you;
      $scope.$apply();
    });
  };

  $scope.update_password = function() {
    let obj = {
      oldpassword: $scope.oldpassword_input,
      password: $scope.password_input,
      confirmpassword: $scope.confirmpassword_input
    };
    utils.disable_action_items();
    client.send_request("/update_password", "PUT", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      $scope.oldpassword_input = '';
      $scope.password_input = '';
      $scope.confirmpassword_input = '';
      $scope.$apply();
    });
  };

  $scope.update_icon = function() {
    let input = document.getElementById('icon_file_input');
    let file = input.files[0];
    if(!file) {
      utils.toast_notification({ message: "No file submitted" });
      return;
    }

    let formData = new FormData();
    formData.append("icon_file", file);

    utils.disable_action_items();
    client.send_request("/update_icon", "PUT", formData, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      $scope.you = resp.you;
      document.getElementById('icon_file_input').value = '';
      $scope.$apply();
    });
  };

  $scope.create_task = function() {
    const obj = {
      taskname: $scope.taskname_input && $scope.taskname_input.trim() || '',
      taskduedate: $scope.taskduedate_input && $scope.taskduedate_input.toJSON().split('T')[0] || '',
    };
    if ($scope.parentTask) {
      obj.parent_task = $scope.parentTask;
      obj.parent_task_id = $scope.parentTask.id;
    }
    utils.disable_action_items();
    client.send_request("/create_task", "POST", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      $scope.taskname_input = '';
      $scope.taskduedate_input = '';
      if ($scope.parentTask) {
        $scope.parentTask.subtasks.unshift(resp.new_task);
        $scope.parentTask = null;
        $scope.isCreatingSubTask = false;
      } else {
        $scope.tasks.unshift(resp.new_task);
        $scope.you.tasks_len++;
      }
      $scope.apply_tasks_filter();
      $scope.$apply();
    });
  };

  $scope.submit_edit_task = function() {
    const obj = {
      taskname: $scope.taskname_input && $scope.taskname_input.trim() || '',
      taskduedate: $scope.taskduedate_input && $scope.taskduedate_input.toJSON().split('T')[0] || '',
      task_id: $scope.editingTask.id
    };
    utils.disable_action_items();
    client.send_request("/update_task", "PUT", obj, null)
    .then(function(resp){
      utils.enable_action_items();
      utils.toast_notification(resp);
      if(resp.error) { return; }
      const list = $scope.get_scope_tasks_list();
      let index = list.indexOf($scope.editingTask);
      list[index] = resp.task;
      $scope.cancel_edit();
      $scope.apply_tasks_filter();
      $scope.$apply();

      let task_elm_id = "#task_" + resp.task.unique_value;
      $('html, body').animate({
  			scrollTop: $(task_elm_id).offset().top - 75
  		}, 1000);
    });
  };

  $scope.edit_task = function(task) {
    $scope.cancel_subtask();
    $scope.editingTask = task;
    $scope.isEditingTask = true;
    $scope.taskname_input = task.text;
    if(task.due_date) {
      let due_date = new Date(task.due_date);
      $scope.taskduedate_input = due_date;
    }
    else {
      $scope.taskduedate_input = null;
    }
    $('html, body').animate({
      scrollTop: $("#create_task_box").offset().top - 75
    }, 1000);
  };

  $scope.create_sub_task = function(task) {
    $scope.cancel_edit();
    $scope.parentTask = task;
    $scope.isCreatingSubTask = true;
    
    $('html, body').animate({
      scrollTop: $("#create_task_box").offset().top - 75
    }, 1000);
  };

  $scope.push_to_stack = function (task) {

  };

  $scope.see_subtasks = function (task) {
    $scope.cancel_edit();
    $scope.cancel_subtask();
    $scope.taskStack.push(task);
    $scope.currentFilter = $scope.filters.ALL;
    utils.sortBy(task.subtasks, 'id', 'desc');
    $scope.tasks_filtered = task.subtasks;
    
    $('html, body').animate({
      scrollTop: $("#tasks-container").offset().top - 75
    }, 1000);
  };

  $scope.stack_set_previous = function() {
    $scope.taskStack.pop();
    if (!!$scope.taskStack.length) {
      const task = $scope.taskStack[$scope.taskStack.length - 1];
      $scope.currentFilter = $scope.filters.ALL;
      utils.sortBy(task.subtasks, 'id', 'desc');
      $scope.tasks_filtered = task.subtasks;
    }
    else {
      $scope.currentFilter = $scope.filters.ALL;
      $scope.tasks_filtered = $scope.tasks;
    }
  };

  $scope.cancel_edit = function(task) {
    $scope.editingTask = null;
    $scope.isEditingTask = false;
    $scope.taskname_input = '';
    $scope.taskduedate_input = null;
  };

  $scope.cancel_subtask = function(task) {
    $scope.parentTask = null;
    $scope.isCreatingSubTask = false;
    $scope.taskname_input = '';
    $scope.taskduedate_input = null;
  };

  $scope.delete_task = function(task) {
    let ask = window.confirm("Delete this task: " + task.text + "?");
    if(!ask) { return }
    client.send_request("/delete_task", "DELETE", task, null)
    .then(function(resp){
      utils.toast_notification(resp);
      const list = $scope.get_scope_tasks_list();
      let index = list.indexOf(task);
      list.splice(index, 1);
      if (!$scope.taskStack.length) {
        $scope.you.tasks_len = $scope.you.tasks_len - 1;
      }
      $scope.apply_tasks_filter();
      $scope.$apply();
    });
  };

  $scope.toggle_task_done = function(task) {
    client.send_request("/toggle_task_done", "PUT", task, null)
    .then(function(resp){
      const list = $scope.get_scope_tasks_list();
      let index = list.indexOf(task);
      list[index] = resp.task;
      $scope.apply_tasks_filter();
      $scope.$apply();
    });
  };

}]);
