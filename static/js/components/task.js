// https://docs.angularjs.org/guide/component

(function(){

  class TaskClass {
    constructor() {}

    $onInit() {
      this.date_created_str = utils.datetime_formatter(this.task.date_created);
      this.date_due_str = 
        this.task.due_date &&
        utils.datetime_formatter(this.task.due_date);
      this.isPast = utils.check_date_past(this.task.due_date);
      this.isLate = this.isPast && !this.task.done;
      this.isTaskDone = this.isDone();
    }

    edit_task() {
      this.edit(this.task);
    }

    create_subtask() {
      this.createSubtask(this.task);
    }

    delete_task() {
      this.delete(this.task);
    }

    toggle_task_done() {
      this.toggle(this.task);
    }

    see_subtasks() {
      this.seeSubtasks(this.task);
    }

    isDone() {
      return this.task.done;
    }
  }

  const TaskComponent = {
    templateUrl: '/static/html/task.html',
    bindings: {
      task: '<',
      edit: '&',
      createSubtask: '&',
      delete: '&',
      toggle: '&',
      seeSubtasks: '&',
    },
    controller: TaskClass
  };

  App.component('task', TaskComponent);

})();
