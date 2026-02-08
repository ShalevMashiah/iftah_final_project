import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_bloc.dart';
import 'view/pages/video_streams_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => VideoStreamsBloc(),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Video Streams GUI',
        theme: ThemeData.dark(useMaterial3: true).copyWith(
          scaffoldBackgroundColor: const Color(0xFF121212),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF1E1E1E),
          ),
        ),
        home: const VideoStreamsPage(),
      ),
    );
  }
}
