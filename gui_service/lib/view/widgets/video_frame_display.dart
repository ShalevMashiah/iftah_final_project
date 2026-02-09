import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';

/// Displays a single video frame with automatic refresh and frame caching
class VideoFrameDisplay extends StatefulWidget {
  final String imagePath;
  final int frameKey;

  const VideoFrameDisplay({
    super.key,
    required this.imagePath,
    required this.frameKey,
  });

  @override
  State<VideoFrameDisplay> createState() => _VideoFrameDisplayState();
}

class _VideoFrameDisplayState extends State<VideoFrameDisplay> {
  Uint8List? _lastSuccessfulFrame;
  bool _isLoading = true;
  bool _isLoadingFrame = false;

  @override
  void didUpdateWidget(VideoFrameDisplay oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.frameKey != widget.frameKey && !_isLoadingFrame) {
      _loadFrame();
    }
  }

  @override
  void initState() {
    super.initState();
    _loadFrame();
  }

  void _loadFrame() {
    // Prevent concurrent reads
    if (_isLoadingFrame) return;
    
    _isLoadingFrame = true;
    
    // Read file synchronously to avoid delays
    try {
      final file = File(widget.imagePath);
      if (file.existsSync()) {
        final bytes = file.readAsBytesSync();
        if (bytes.isNotEmpty && mounted) {
          setState(() {
            _lastSuccessfulFrame = bytes;
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      // Keep showing last successful frame on error
      // Don't change state if we have a cached frame
    } finally {
      _isLoadingFrame = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_lastSuccessfulFrame != null) {
      return Image.memory(
        _lastSuccessfulFrame!,
        fit: BoxFit.contain,
        gaplessPlayback: true,
        filterQuality: FilterQuality.low, // Faster rendering
        errorBuilder: (context, error, stackTrace) {
          // Even on decode error, keep showing the widget (will use last frame)
          return Container(color: Colors.black);
        },
      );
    }

    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(color: Colors.blue),
            const SizedBox(height: 8),
            Text(
              'Waiting for frames...',
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
          ],
        ),
      );
    }

    return Container(color: Colors.black);
  }
}
