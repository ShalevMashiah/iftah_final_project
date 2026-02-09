import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_event.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_state.dart';
import '../widgets/streams_status_bar.dart';
import '../widgets/streams_grid_view.dart';

class VideoStreamsPage extends StatelessWidget {
  const VideoStreamsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Streams'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<VideoStreamsBloc>().add(const LoadStreamsEvent());
            },
          ),
        ],
      ),
      body: BlocBuilder<VideoStreamsBloc, VideoStreamsState>(
        builder: (context, state) {
          if (state is VideoStreamsInitial) {
            context.read<VideoStreamsBloc>().add(const LoadStreamsEvent());
            return const Center(child: CircularProgressIndicator());
          }

          final streams = state.streams;

          if (streams.isEmpty) {
            return const Center(
              child: Text(
                'No streams available',
                style: TextStyle(fontSize: 16),
              ),
            );
          }

          return Column(
            children: [
              StreamsStatusBar(
                totalStreams: state.streams.length,
                activeStreams: state.activeStreams.length,
                inactiveStreams: state.inactiveStreams.length,
              ),
              Expanded(
                child: StreamsGridView(streams: streams),
              ),
            ],
          );
        },
      ),
    );
  }
}
