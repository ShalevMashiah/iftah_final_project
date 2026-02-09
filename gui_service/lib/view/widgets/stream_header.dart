import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_bloc.dart';
import 'package:flutter_to_do_list/bloc/video_streams/video_streams_event.dart';

/// Header widget for video stream displaying title, status, and motion detection
class StreamHeader extends StatelessWidget {
  final VideoStream stream;

  const StreamHeader({
    super.key,
    required this.stream,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Row(
        children: [
          Icon(
            Icons.videocam,
            color: stream.isActive ? Colors.green : Colors.red,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            stream.title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const Spacer(),
          // Record button
          IconButton(
            icon: Icon(
              stream.isRecording ? Icons.stop_circle : Icons.fiber_manual_record,
              color: stream.isRecording ? Colors.red : Colors.white,
            ),
            tooltip: stream.isRecording ? 'Stop Recording' : 'Start Recording',
            onPressed: () {
              if (stream.isRecording) {
                context.read<VideoStreamsBloc>().add(StopRecordingEvent(stream.id));
              } else {
                context.read<VideoStreamsBloc>().add(StartRecordingEvent(stream.id));
              }
            },
          ),
          const SizedBox(width: 8),
          if (stream.motionDetections != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Motion: ${stream.motionDetections}',
                style: const TextStyle(color: Colors.orange, fontSize: 12),
              ),
            ),
          const SizedBox(width: 8),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: stream.isActive ? Colors.green : Colors.red,
            ),
          ),
        ],
      ),
    );
  }
}
