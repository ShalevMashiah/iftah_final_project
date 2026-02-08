import 'package:flutter_to_do_list/domain/model/data_classes/todo.dart';

abstract class TodoListEvent {
  const TodoListEvent();
}

class AddTodoEvent extends TodoListEvent {
  final Todo todo;
  const AddTodoEvent(this.todo);
}

class ToggleTodoEvent extends TodoListEvent {
  final String id;
  const ToggleTodoEvent(this.id);
}

class DeleteTodoEvent extends TodoListEvent {
  final String id;
  const DeleteTodoEvent(this.id);
}

class EditTodoEvent extends TodoListEvent {
  final String id;
  final String newTitle;
  final String newDescription;

  const EditTodoEvent({
    required this.id,
    required this.newTitle,
    required this.newDescription,
  });
}
