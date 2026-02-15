import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
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
  ui.Image? _lastImage;
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
    if (_isLoadingFrame) return;
    _isLoadingFrame = true;

    () async {
      try {
        final file = File(widget.imagePath);
        if (!await file.exists()) return;
        final bytes = await file.readAsBytes();
        if (bytes.isEmpty || !mounted) return;

        // Decode image using engine (non-blocking to Dart UI thread)
        final codec = await ui.instantiateImageCodec(bytes);
        final frameInfo = await codec.getNextFrame();
        final ui.Image image = frameInfo.image;

        // Dispose previous image to avoid leaks
        _lastImage?.dispose();

        if (mounted) {
          setState(() {
            _lastImage = image;
            _isLoading = false;
          });
        } else {
          image.dispose();
        }
      } catch (e) {
        // ignore errors and keep last image
      } finally {
        _isLoadingFrame = false;
      }
    }();
  }

  @override
  Widget build(BuildContext context) {
    if (_lastImage != null) {
      return RawImage(
        image: _lastImage,
        fit: BoxFit.contain,
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

  @override
  void dispose() {
    _lastImage?.dispose();
    super.dispose();
  }
}
