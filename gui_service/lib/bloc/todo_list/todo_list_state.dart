import 'package:equatable/equatable.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/todo.dart';

abstract class TodoListState extends Equatable {
  final List<Todo> todos;
  const TodoListState(this.todos);

  List<Todo> get completed => todos.where((t) => t.isDone).toList();
  List<Todo> get pending => todos.where((t) => !t.isDone).toList();

  @override
  List<Object?> get props => [todos];
}

class TodoListInitial extends TodoListState {
  const TodoListInitial() : super(const []);
}

class TodoListLoaded extends TodoListState {
  const TodoListLoaded(List<Todo> todos) : super(todos);
}
