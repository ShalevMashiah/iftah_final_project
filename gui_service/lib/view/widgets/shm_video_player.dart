import 'dart:io';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

/// Simple wrapper around `video_player` to play local SHM/AVI files.
class ShmVideoPlayer extends StatefulWidget {
  final String path;
  final bool autoplay;
  final bool looping;

  const ShmVideoPlayer({super.key, required this.path, this.autoplay = true, this.looping = true});

  @override
  State<ShmVideoPlayer> createState() => _ShmVideoPlayerState();
}

class _ShmVideoPlayerState extends State<ShmVideoPlayer> {
  VideoPlayerController? _controller;
  Future<void>? _initializeFuture;

  @override
  void initState() {
    super.initState();
    _initController();
  }

  void _initController() {
    try {
      final file = File(widget.path);
      if (file.existsSync()) {
        _controller = VideoPlayerController.file(file);
        _controller!..setLooping(widget.looping);
        _initializeFuture = _controller!.initialize().then((_) {
          if (widget.autoplay) _controller!.play();
          setState(() {});
        });
      } else {
        // File doesn't exist; leave controller null so caller can fallback
        _controller = null;
      }
    } catch (e) {
      // ignore init errors
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null) {
      return const Center(child: Text('No video', style: TextStyle(color: Colors.white)));
    }

    return FutureBuilder<void>(
      future: _initializeFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done && _controller!.value.isInitialized) {
          return AspectRatio(
            aspectRatio: _controller!.value.aspectRatio,
            child: VideoPlayer(_controller!),
          );
        }

        return const Center(child: CircularProgressIndicator());
      },
    );
  }
}
