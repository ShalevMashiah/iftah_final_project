import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Custom image provider that reads file directly without caching
/// Used for video frame streaming from continuously updated JPG files
class FileVideoImageProvider extends ImageProvider<FileVideoImageProvider> {
  final String filePath;
  final int frameKey;

  const FileVideoImageProvider(this.filePath, {required this.frameKey});

  @override
  Future<FileVideoImageProvider> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<FileVideoImageProvider>(this);
  }

  @override
  ImageStreamCompleter loadImage(FileVideoImageProvider key, ImageDecoderCallback decode) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
      debugLabel: filePath,
      informationCollector: () => <DiagnosticsNode>[
        DiagnosticsProperty<ImageProvider>('Image provider', this),
        DiagnosticsProperty<FileVideoImageProvider>('Image key', key),
      ],
    );
  }

  Future<ui.Codec> _loadAsync(FileVideoImageProvider key, ImageDecoderCallback decode) async {
    try {
      final File file = File(key.filePath);
      final Uint8List bytes = await file.readAsBytes();
      
      if (bytes.isEmpty) {
        throw Exception('File is empty: ${key.filePath}');
      }

      final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
      return decode(buffer);
    } catch (e) {
      // Return a 1x1 transparent image on error
      final Uint8List emptyImage = Uint8List.fromList([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89,
        0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01,
        0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
      ]);
      final buffer = await ui.ImmutableBuffer.fromUint8List(emptyImage);
      return decode(buffer);
    }
  }

  @override
  bool operator ==(Object other) {
    if (other.runtimeType != runtimeType) return false;
    return other is FileVideoImageProvider && 
           other.filePath == filePath && 
           other.frameKey == frameKey;
  }

  @override
  int get hashCode => Object.hash(filePath, frameKey);

  @override
  String toString() => '${objectRuntimeType(this, 'FileVideoImageProvider')}("$filePath", frameKey: $frameKey)';
}
