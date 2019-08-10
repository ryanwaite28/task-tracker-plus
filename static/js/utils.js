const utils = {};

/**/

utils.capitalize = function(string) {
  let str = string.toLowerCase();
  return str.charAt(0).toUpperCase() + str.slice(1);
};

utils.enable_action_items = function() {
  $('.action-item').show();
};

utils.disable_action_items = function() {
  $('.action-item').hide();
};

utils.array_sort_by = function(array, property, direction) {
  let tempArray = array;
  tempArray.sort(function(a, b){
    var x = a[property].constructor === String && a[property].toLowerCase() || a[property];
    var y = b[property].constructor === String && b[property].toLowerCase() || b[property];
    let value = direction && String(direction) || "asc";
    switch(value) {
      case "asc":
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
      case "desc":
        // desc
        if (x > y) {return -1;}
        if (x < y) {return 1;}
        return 0;
      default:
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
    }
  });
  return tempArray;
};

utils.validateURL = function(link) {
  if(!link) { return false; }
  if(link.constructor !== String) { return false; }
	var re = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
	return re.test(link.toLowerCase());
};

utils.date_formatter = function(date) {
  return moment(date).format('MMMM D, YYYY');
};
utils.datetime_formatter = function(date) {
  return moment(date).format('MMMM D, YYYY - h:mm A');
};

utils.toast_notification = function(data) {
  let unique_value = String(Date.now()) + Math.random().toString(36).substr(2, 34);
  let notify_dom_str = '<div id="' + unique_value + '" class="ui hidden message notify_block"> \
    <i class="close icon"></i> \
    <div class="header" id="notify_header_' + unique_value + '">' + (data.header || "Notification") + '</div> \
    <p id="notify_message_' + unique_value + '">' + data.message + '</p> \
  </div>';
  let notify_dom = $(notify_dom_str);
  $('#notify_container').prepend(notify_dom);
  let id = '#' + unique_value;
  let get_notify_dom = $(id);
  get_notify_dom.removeClass('hidden');
  setTimeout(function(){
    get_notify_dom.find('.close').trigger('click');
    setTimeout(function(){ get_notify_dom.remove(); }, 2000)
  }, 5000);
};

utils.check_date_past = function (date) {
  if (!date) {
    return false;
  }
  const now = new Date();
  const due = new Date(date);
  const isPast = now >= due;
  return isPast;
};

utils.filters = Object.freeze({
  "ALL": "ALL",
  "DONE": "DONE",
  "NOT_DONE": "NOT_DONE",
  "LATE": "LATE",
  "DUE_TODAY": "DUE_TODAY",
  "ON_TIME": "ON_TIME",
  "NO_DUE_DATE": "NO_DUE_DATE",
});

utils.determine_time_status = function(task) {
  if (!task.due_date) {
    return this.filters.NO_DUE_DATE;
  }
  
  const now = new Date();
  const due = new Date(task.due_date);

  const isPast = now > due;
  const isOnTime = now < due;
  const isDueToday = (() => {
    const nowDay = now.getDate();
    const nowMonth = now.getMonth();
    const nowYear = now.getFullYear();
    const dueDay = due.getDate();
    const dueMonth = due.getMonth();
    const dueYear = due.getFullYear();
    const isSameDay = (
      nowDay === dueDay &&
      nowMonth === dueMonth &&
      nowYear === dueYear
    );
    return isSameDay;
  })();

  if (isPast) {
    return this.filters.LATE;
  }
  if (isOnTime) {
    if (isDueToday) {
      return this.filters.DUE_TODAY;
    }
    return this.filters.ON_TIME;
  }
};

utils.sortBy = function(list, property, direction, isDateString) {
  list.sort(function(a, b){
    let x, y;
    if(isDateString === true) {
      x = new Date(a[property]);
      y = new Date(b[property]);
    } else {
      x = a[property].constructor === String && a[property].toLowerCase() || a[property];
      y = b[property].constructor === String && b[property].toLowerCase() || b[property];
    }
    let value = direction && String(direction) || "asc";
    switch(value) {
      case "asc":
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
      case "desc":
        // desc
        if (x > y) {return -1;}
        if (x < y) {return 1;}
        return 0;
      default:
        // asc
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
    }
  });
  return list;
};

/**/

Object.freeze(utils);
