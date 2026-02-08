import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';

abstract class VideoStreamsEvent {
  const VideoStreamsEvent();
}

class LoadStreamsEvent extends VideoStreamsEvent {
  const LoadStreamsEvent();
}

class UpdateStreamStatusEvent extends VideoStreamsEvent {
  final String streamId;
  final bool isActive;
  final int? motionDetections;

  const UpdateStreamStatusEvent({
    required this.streamId,
    required this.isActive,
    this.motionDetections,
  });
}

class AddStreamEvent extends VideoStreamsEvent {
  final VideoStream stream;
  const AddStreamEvent(this.stream);
}

class RemoveStreamEvent extends VideoStreamsEvent {
  final String streamId;
  const RemoveStreamEvent(this.streamId);
}
