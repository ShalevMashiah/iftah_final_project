import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';
import 'stream_header.dart';
import 'stream_status_widget.dart';
import 'video_frame_display.dart';

class VideoStreamWidget extends StatefulWidget {
  final VideoStream stream;

  const VideoStreamWidget({
    super.key,
    required this.stream,
  });

  @override
  State<VideoStreamWidget> createState() => _VideoStreamWidgetState();
}

class _VideoStreamWidgetState extends State<VideoStreamWidget> {
  Timer? _refreshTimer;
  int _frameKey = 0;

  @override
  void initState() {
    super.initState();
    // Refresh at 30 FPS to match algorithm service output
    _refreshTimer = Timer.periodic(const Duration(milliseconds: 33), (_) {
      if (mounted) {
        setState(() {
          _frameKey++;
        });
      }
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: widget.stream.isActive
              ? Colors.green.withOpacity(0.5)
              : Colors.red.withOpacity(0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          StreamHeader(stream: widget.stream),
          const Divider(height: 1, color: Color(0xFF333333)),
          _buildStreamContent(),
        ],
      ),
    );
  }

  Widget _buildStreamContent() {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: Container(
        color: Colors.black,
        child: widget.stream.isActive
            ? VideoFrameDisplay(
                imagePath: widget.stream.streamUrl,
                frameKey: _frameKey,
              )
            : const StreamInactiveWidget(),
      ),
    );
  }
}
