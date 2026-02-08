import 'package:equatable/equatable.dart';

/// Data model representing a video stream
class VideoStream extends Equatable {
  final String id;
  final String title;
  final String streamUrl;
  final bool isActive;
  final DateTime? lastUpdate;
  final int? motionDetections;

  const VideoStream({
    required this.id,
    required this.title,
    required this.streamUrl,
    this.isActive = false,
    this.lastUpdate,
    this.motionDetections,
  });

  VideoStream copyWith({
    String? id,
    String? title,
    String? streamUrl,
    bool? isActive,
    DateTime? lastUpdate,
    int? motionDetections,
  }) {
    return VideoStream(
      id: id ?? this.id,
      title: title ?? this.title,
      streamUrl: streamUrl ?? this.streamUrl,
      isActive: isActive ?? this.isActive,
      lastUpdate: lastUpdate ?? this.lastUpdate,
      motionDetections: motionDetections ?? this.motionDetections,
    );
  }

  @override
  List<Object?> get props => [id, title, streamUrl, isActive, lastUpdate, motionDetections];
}
