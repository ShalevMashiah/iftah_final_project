import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';

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
  int _refreshKey = 0;

  @override
  void initState() {
    super.initState();
    // Refresh image every ~33ms for 30 FPS (matching algorithm service frame rate)
    _refreshTimer = Timer.periodic(const Duration(milliseconds: 33), (timer) {
      if (mounted) {
        setState(() {
          _refreshKey++;
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
          _buildHeader(),
          const Divider(height: 1, color: Color(0xFF333333)),
          _buildStreamContent(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Row(
        children: [
          Icon(
            Icons.videocam,
            color: widget.stream.isActive ? Colors.green : Colors.red,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            widget.stream.title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const Spacer(),
          if (widget.stream.motionDetections != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Motion: ${widget.stream.motionDetections}',
                style: const TextStyle(color: Colors.orange, fontSize: 12),
              ),
            ),
          const SizedBox(width: 8),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: widget.stream.isActive ? Colors.green : Colors.red,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStreamContent() {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: Container(
        color: Colors.black,
        child: widget.stream.isActive ? _buildVideoFrame() : _buildInactiveWidget(),
      ),
    );
  }

  Widget _buildVideoFrame() {
    final imagePath = widget.stream.streamUrl;
    final file = File(imagePath);

    // Read file bytes directly and create image from memory
    // This bypasses Flutter's file image cache
    return FutureBuilder<Uint8List>(
      key: ValueKey(_refreshKey),
      future: file.readAsBytes(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done && 
            snapshot.hasData && 
            snapshot.data!.isNotEmpty) {
          return Image.memory(
            snapshot.data!,
            fit: BoxFit.contain,
            gaplessPlayback: true,
          );
        }
        
        if (snapshot.hasError) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.image_not_supported, color: Colors.orange, size: 48),
                const SizedBox(height: 8),
                Text(
                  'Waiting for frames...',
                  style: const TextStyle(color: Colors.white70),
                ),
              ],
            ),
          );
        }
        
        // Loading state
        return const Center(
          child: CircularProgressIndicator(),
        );
      },
    );
  }

  Widget _buildInactiveWidget() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.videocam_off, color: Colors.red, size: 48),
          SizedBox(height: 8),
          Text(
            'Stream Inactive',
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorWidget() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: Colors.red, size: 48),
          SizedBox(height: 8),
          Text(
            'Stream Error',
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    );
  }
}
