import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/bloc/todo_list/todo_list_bloc.dart';
import 'package:flutter_to_do_list/bloc/todo_list/todo_list_event.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/todo.dart';

class TodoItemWidget extends StatelessWidget {
  final Todo todo;

  const TodoItemWidget({
    super.key,
    required this.todo,
  });

  String _format(DateTime? date) {
    if (date == null) return "N/A";
    return date.toString().substring(0, 16);
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: ListTile(
        title: Text(
          todo.title,
          style: TextStyle(
            decoration: todo.isDone ? TextDecoration.lineThrough : null,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(todo.description),
        leading: Checkbox(
          value: todo.isDone,
          onChanged: (_) {
            if (!todo.isDone) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text("Task completed at ${_format(DateTime.now())}"),
                ),
              );
            }

            context.read<TodoListBloc>().add(ToggleTodoEvent(todo.id));
          },
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              todo.isDone
                  ? 'Completed at ${_format(todo.completedAt)}'
                  : 'Created at ${_format(todo.createdAt)}',
              style: TextStyle(
                color: todo.isDone ? Colors.green : Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => _showEditDialog(context, todo),
            ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: () {
                context.read<TodoListBloc>().add(DeleteTodoEvent(todo.id));
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showEditDialog(BuildContext context, Todo todo) {
    final titleController = TextEditingController(text: todo.title);
    final descController = TextEditingController(text: todo.description);

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Edit Task'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            TextField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<TodoListBloc>().add(
                    EditTodoEvent(
                      id: todo.id,
                      newTitle: titleController.text,
                      newDescription: descController.text,
                    ),
                  );
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
