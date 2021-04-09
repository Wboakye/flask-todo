import datetime as dt
import json

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy import exc

from models import db, ToDo
from services import order_todo_items
from filters import friendly_date

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        todos = ToDo.query.filter_by(user_id=current_user.id)
        todo_order = json.loads(current_user.todo_order)
        ordered_todos = order_todo_items(todo_order, todos)

        return render_template("todo.html", todos=ordered_todos, current_page="home")
    else:
        return render_template("login.html", current_page="login")


@main.route("/add_todo", methods=["POST"])
@login_required
def add_todo():
    user_id = current_user.id
    task = request.form.get("task").strip()
    due_date_str = request.form.get("dueDate")

    due_date = dt.datetime.strptime(due_date_str, "%Y-%m-%d")

    new_todo = ToDo(task=task, user_id=user_id, due_date=due_date)
    db.session.add(new_todo)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({"success": False})

    # Update user's todo order
    todo_order = json.loads(current_user.todo_order)
    todo_order.append(str(new_todo.id))
    current_user.todo_order = json.dumps(todo_order)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        # If unable to update user table,
        # delete new todo, throw error to user
        db.session.delete(new_todo)
        db.session.commit()
        return jsonify({"success": False})

    return_data = {
        "success": True,
        "todo": {
            "id": new_todo.id,
            "task": new_todo.task,
            "dueDate": friendly_date(new_todo.due_date),
            "completed": new_todo.completed,
        },
    }

    return jsonify(return_data)


@main.route("/edit_todo", methods=["POST"])
@login_required
def edit_todo():
    todo_id = request.form.get("id")
    task = request.form.get("task")

    todo = ToDo.query.filter_by(id=int(todo_id)).first()
    todo.task = task

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({"success": False})

    return jsonify({"success": True})


@main.route("/delete_todo", methods=["POST"])
@login_required
def delete_todo():
    todo_id = request.form.get("id")
    todo = ToDo.query.filter_by(id=int(todo_id)).first()
    db.session.delete(todo)

    todo_order = json.loads(current_user.todo_order)
    todo_order.remove(todo_id)
    current_user.todo_order = json.dumps(todo_order)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({"success": False})

    return jsonify({"success": True})


@main.route("/update_todo_order", methods=["POST"])
@login_required
def update_todo_order():
    todo_id = request.form.get("id")
    direction = request.form.get("direction")

    todo_order = json.loads(current_user.todo_order)
    todo_count = len(todo_order)

    current_index = todo_order.index(todo_id)

    if direction == "up":
        new_index = current_index - 1
    else:
        new_index = current_index + 1

    if (direction == "up" and new_index < 0) or (
        direction == "down" and new_index >= todo_count
    ):
        return jsonify({"success": True, "change": False})

    displaced_item = todo_order[new_index]
    todo_order[new_index] = todo_id
    todo_order[current_index] = displaced_item
    current_user.todo_order = json.dumps(todo_order)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({"success": False})

    todo = ToDo.query.filter_by(id=int(todo_id)).first()
    completed = todo.completed
    task = todo.task
    due_date = friendly_date(todo.due_date)

    print(due_date)

    return_data = {
        "success": True,
        "change": True,
        "task": task,
        "completed": completed,
        "dueDate": due_date,
    }

    return jsonify(return_data)


@main.route("/mark_complete", methods=["POST"])
@login_required
def mark_complete():
    todo_id = request.form.get("id")
    completed = request.form.get("completed")

    todo = ToDo.query.filter_by(id=int(todo_id)).first()

    todo.completed = bool(completed)
    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return jsonify({"success": False})

    return jsonify({"success": True})
