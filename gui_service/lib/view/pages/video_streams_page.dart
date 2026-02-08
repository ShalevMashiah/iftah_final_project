import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_event.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_state.dart';
import '../widgets/video_stream_widget.dart';

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
              _buildStatusBar(state),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final isWide = constraints.maxWidth >= 900;
                      
                      if (isWide) {
                        return Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: streams.map((stream) {
                            return Expanded(
                              child: Padding(
                                padding: const EdgeInsets.only(right: 12),
                                child: VideoStreamWidget(stream: stream),
                              ),
                            );
                          }).toList(),
                        );
                      } else {
                        return SingleChildScrollView(
                          child: Column(
                            children: streams.map((stream) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: VideoStreamWidget(stream: stream),
                              );
                            }).toList(),
                          ),
                        );
                      }
                    },
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildStatusBar(VideoStreamsState state) {
    return Container(
      padding: const EdgeInsets.all(12),
      color: const Color(0xFF1E1E1E),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildStatusItem(
            'Total Streams',
            state.streams.length.toString(),
            Colors.blue,
          ),
          _buildStatusItem(
            'Active',
            state.activeStreams.length.toString(),
            Colors.green,
          ),
          _buildStatusItem(
            'Inactive',
            state.inactiveStreams.length.toString(),
            Colors.red,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusItem(String label, String value, Color color) {
    return Row(
      children: [
        Icon(Icons.circle, color: color, size: 12),
        const SizedBox(width: 8),
        Text(
          '$label: $value',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
