import 'package:flutter/material.dart';

/// Widget displayed when stream is inactive
class StreamInactiveWidget extends StatelessWidget {
  const StreamInactiveWidget({super.key});

  @override
  Widget build(BuildContext context) {
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
}

/// Widget displayed when stream has an error
class StreamErrorWidget extends StatelessWidget {
  const StreamErrorWidget({super.key});

  @override
  Widget build(BuildContext context) {
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
