function create_list_item (id, task, dueDate, completed=false) {
    let li = document.createElement('li');
    let completion_attribute = completed ? 'checked' : ''
    let innerHtml = `
                <div class="form-check"> 
                    <div class="row">
                        <div class="col-sm-9">
                            <label class="form-check-label mt-1">
                                <input id="check-${ id }" class="checkbox mr-1" type="checkbox" ${completion_attribute}> <label for="task-${id}" id="task-${id}" class="task"><i class="task-date">${dueDate}</i>: ${task}</label>
                            </label> 
                        </div>
                        <div class="col-sm-3">
                            <div class="btn-group btn-group-sm mt-1" role="group" aria-label="action buttons">
                                <button type="button" class="btn btn-secondary up-button" onClick="moveItem(${ id }, 'up')"><i class="fas fa-angle-up"></i></button>
                                <button type="button" class="btn btn-secondary down-button" onClick="moveItem(${ id }, 'down')"><i class="fas fa-angle-down"></i></button>
                                <button type="button" class="btn btn-secondary" onClick="editItemModal(${ id })"><i class="far fa-edit"></i></button>
                                <button type="button" class="btn btn-secondary" onClick="deleteItemModal(${ id })"><i class="fas fa-times"></i></button>
                              </div>
                        </div>
                        
                    </div>
                </div> 
    
    `
    li.id = `todo-item-${id}`;
    li.className = `list-group-item`;
    li.innerHTML = innerHtml;

    return li
}


function addItem(){
    
    let toDoInput = document.querySelector("#toDoInput");
    let todoList = document.querySelector("#todo-list");
    let dueDate = document.querySelector('#task-due-date').value;
    const task = toDoInput.value;

    if(!dueDate){
        dueDate = moment().format('YYYY-MM-DD')
    }


    if (!task) {
        // Do nothing
        return
    }

    if(task.length > 280){
        $("#character-count-error-modal").modal("show");
        return
    }

    let data = {
        "task": task,
        "dueDate": dueDate,
    };

    $.ajax({
        url: '/add_todo',
        type: 'POST',
        dataType: 'JSON',
        data: data,
        success: function (data) {
          if(!data.success){
            $("#errorModal").modal("show")
            return
          }
          const id = data.todo.id;
          const task = data.todo.task;
          const dueDate = data.todo.dueDate

          let li = create_list_item(id, task, dueDate)
          todoList.append(li)
          toDoInput.value = '';
        },
        error: function (request, status, error) {
            $("#errorModal").modal("show")
            console.log('error time: ' + error);
          }
      })

}


function moveItem (id, direction) {
    let buttons = document.querySelectorAll(`.${direction}-button`);

    for (let i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }

    const data = {
        "id": id,
        "direction": direction
    }

    $.ajax({
        url: '/update_todo_order',
        type: 'POST',
        dataType: 'JSON',
        data: data,
        success: function (data) {
          if(data.success && data.change){
            let currentItem = document.querySelector(`#todo-item-${id}`);
            let itemCopy = create_list_item(id, data.task, data.dueDate, data.completed);
            let displacedItem;
            // Get displaced item remove current item and insert a copy of removed item 
            if (direction == 'up'){
                displacedItem = currentItem.previousElementSibling;
                displacedItem.parentNode.removeChild(currentItem);
                displacedItem.parentNode.insertBefore(itemCopy, displacedItem);
            } else {
                displacedItem = currentItem.nextElementSibling;
                displacedItem.parentNode.removeChild(currentItem);
                displacedItem.after(itemCopy);
            }
            
          }
          for (let i = 0; i < buttons.length; i++) {
            buttons[i].disabled = false;
          }
          if(!data.success){
            $("#errorModal").modal("show");
            return
          }

        },
        error: function (request, status, error) {
            $("#errorModal").modal("show");
            console.log('error time: ' + error);
          }
      })

}


function editItemModal (id) {
    let task = document.querySelector(`#task-${id}`).innerText;
    let input = document.querySelector('#editTodoInput');
    let editTodoId = document.querySelector("#edit-todo-id");

    input.value = task;
    editTodoId.value = id;

    $("#edit-task-modal").modal("show");
}


function deleteItemModal (id) {
    let editTodoId = document.querySelector("#edit-todo-id");
    editTodoId.value = id;

    $("#delete-task-modal").modal("show");

}

function editItem () {
    let input = document.querySelector('#editTodoInput').value;
    let id = document.querySelector("#edit-todo-id").value;
    let task = document.querySelector(`#task-${id}`)

    const data = {
        "id": id,
        "task": input,
    }

    $.ajax({
        url: '/edit_todo',
        type: 'POST',
        dataType: 'JSON',
        data: data,
        success: function (data) {
          if(data.success){
            task.innerText = input
            $("#edit-task-modal").modal("hide");
          }else{
            $("#edit-task-modal").modal("hide");
            $("#errorModal").modal("show");
          }
          

        },
        error: function (request, status, error) {
            console.log('error time: ' + error);
            $("#edit-task-modal").modal("hide");
            $("#errorModal").modal("show");
          }
      })
}

function deleteItem(){
    let id = document.querySelector("#edit-todo-id").value;
    let todo = document.querySelector(`#todo-item-${id}`);

    const data = {
        "id": id,
    }

    $.ajax({
        url: '/delete_todo',
        type: 'POST',
        dataType: 'JSON',
        data: data,
        success: function (data) {
          if(data.success){
            todo.parentNode.removeChild(todo)
            $("#delete-task-modal").modal("hide");
          } else {
            $("#delete-task-modal").modal("hide");
            $("#errorModal").modal("show");
          }
        },
        error: function (request, status, error) {
            console.log('error time: ' + error);
            $("#edelete-task-modal").modal("hide");
            $("#errorModal").modal("show");
          }
      })
}

function markComplete (id) {
    let checkbox = document.querySelector(`#check-${id}`);
    checkbox.disabled = true;

    const data = {
        "id": id,
        "completed": checkbox.checked
    }

    $.ajax({
        url: '/mark_complete',
        type: 'POST',
        dataType: 'JSON',
        data: data,
        success: function (data) {
          if(data.success){
            checkbox.disabled = false;
          } else {
            checkbox.checked = !checkbox.checked
            checkbox.disabled = false;
            $("#errorModal").modal("show");
          }
        },
        error: function (request, status, error) {
            console.log('error time: ' + error);
            checkbox.checked = !checkbox.checked
            checkbox.disabled = false;
            $("#errorModal").modal("show");
          }
      })

}

function initDatePickers() {
    let dateRangePicker = document.querySelector('#date-range-picker');
    if (dateRangePicker){
        
        $('#date-range-picker').daterangepicker({
            singleDatePicker: true,
            opens: 'left',
            buttonClasses: ['btn btn-default'],
            applyClass: 'btn-small btn-primary',
            showDropdowns: true,
            startDate: moment(),
            minYear: parseInt(moment().format('YYYY'),10),
          }, function(start, end, label) {
            let startStr = start.format('YYYY-MM-DD');
            let dateHolder = document.querySelector("#task-due-date")
            dateHolder.value = startStr;
          });

    }
}

function openDateRangePicker(){
    $('#date-range-picker').data('daterangepicker').toggle();
}

function comparePasswords(){
    let password1 = document.querySelector('#password').value
    let password2 = document.querySelector('#password2').value
    let errorMessage = document.querySelector('#password_mismatch_error_message')
    let newUserForm = document.querySelector('#new-user-form')
    
    errorMessage.style.display = "none"
    if(password1 != password2){
        errorMessage.style.display="block";
        return
    }
    console.log('submit')
    newUserForm.submit()
}


$(document).ready(function () {
    initDatePickers()
  })