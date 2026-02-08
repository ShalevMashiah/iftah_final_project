import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/bloc/todo_list/todo_list_bloc.dart';
import 'view/pages/todo_list_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => TodoListBloc(),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Flutter To-Do List',
        theme: ThemeData(useMaterial3: true),
        home: TodoListPage(),
      ),
    );
  }
}
