def order_todo_items(order, items):
    ordered_items = []
    for o in order:
        # iterate through items, find item with matching id
        todo = next((i for i in items if i.id == int(o)), None)
        ordered_items.append(todo)

    return ordered_items
