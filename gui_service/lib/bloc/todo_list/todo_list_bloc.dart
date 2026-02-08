import 'package:bloc/bloc.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/todo.dart';
import 'todo_list_event.dart';
import 'todo_list_state.dart';

class TodoListBloc extends Bloc<TodoListEvent, TodoListState> {
  TodoListBloc() : super(const TodoListInitial()) {
    _startEventListening();
  }

  void _startEventListening() {
    on<TodoListEvent>((event, emit) {});

    on<AddTodoEvent>((event, emit) {
      final updatedTodos = List<Todo>.of(state.todos)..add(event.todo);
      emit(TodoListLoaded(updatedTodos));
    });

    on<ToggleTodoEvent>((event, emit) {
      final updatedTodos = state.todos.map((todo) {
        if (todo.id == event.id) {
          if (!todo.isDone) {
            return todo.copyWith(
              isDone: true,
              completedAt: DateTime.now(),
            );
          } else {
            return todo.copyWith(
              isDone: false,
              completedAt: null,
            );
          }
        }
        return todo;
      }).toList();

      emit(TodoListLoaded(updatedTodos));
    });

    on<DeleteTodoEvent>((event, emit) {
      final updatedTodos = state.todos.where((todo) => todo.id != event.id).toList();
      emit(TodoListLoaded(updatedTodos));
    });

    on<EditTodoEvent>((event, emit) {
      final updatedTodos = state.todos.map((todo) {
        if (todo.id == event.id) {
          return todo.copyWith(
            title: event.newTitle,
            description: event.newDescription,
          );
        }
        return todo;
      }).toList();

      emit(TodoListLoaded(updatedTodos));
    });
  }
}
