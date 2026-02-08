import 'package:equatable/equatable.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';

abstract class VideoStreamsState extends Equatable {
  final List<VideoStream> streams;
  const VideoStreamsState(this.streams);

  List<VideoStream> get activeStreams => streams.where((s) => s.isActive).toList();
  List<VideoStream> get inactiveStreams => streams.where((s) => !s.isActive).toList();

  @override
  List<Object?> get props => [streams];
}

class VideoStreamsInitial extends VideoStreamsState {
  const VideoStreamsInitial() : super(const []);
}

class VideoStreamsLoaded extends VideoStreamsState {
  const VideoStreamsLoaded(List<VideoStream> streams) : super(streams);
}
