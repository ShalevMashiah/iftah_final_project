import 'package:flutter/material.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';
import 'video_stream_widget.dart';

/// Grid layout for displaying multiple video streams
class StreamsGridView extends StatelessWidget {
  final List<VideoStream> streams;

  const StreamsGridView({
    super.key,
    required this.streams,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
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
    );
  }
}
