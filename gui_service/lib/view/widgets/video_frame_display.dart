import 'package:flutter/material.dart';
import '../../infrastructure/providers/file_video_image_provider.dart';

/// Displays a single video frame with automatic refresh
class VideoFrameDisplay extends StatelessWidget {
  final String imagePath;
  final int frameKey;

  const VideoFrameDisplay({
    super.key,
    required this.imagePath,
    required this.frameKey,
  });

  @override
  Widget build(BuildContext context) {
    return Image(
      image: FileVideoImageProvider(imagePath, frameKey: frameKey),
      fit: BoxFit.contain,
      gaplessPlayback: true,
      errorBuilder: (context, error, stackTrace) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.image_not_supported, color: Colors.orange, size: 48),
              const SizedBox(height: 8),
              Text(
                'Waiting for frames...',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        );
      },
    );
  }
}
