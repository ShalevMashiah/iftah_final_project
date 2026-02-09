import 'package:bloc/bloc.dart';
import 'package:flutter_to_do_list/domain/model/data_classes/video_stream.dart';
import 'video_streams_event.dart';
import 'video_streams_state.dart';
import 'dart:io';

class VideoStreamsBloc extends Bloc<VideoStreamsEvent, VideoStreamsState> {
  VideoStreamsBloc() : super(const VideoStreamsInitial()) {
    _startEventListening();
  }

  void _startEventListening() {
    on<VideoStreamsEvent>((event, emit) {});

    on<LoadStreamsEvent>((event, emit) {
      // Initialize with default streams pointing to shared image files
      final streams = [
        const VideoStream(
          id: '1',
          title: 'Video Stream 1',
          streamUrl: '/app/logs/stream_1.jpg',
          isActive: true,
        ),
        const VideoStream(
          id: '2',
          title: 'Video Stream 2',
          streamUrl: '/app/logs/stream_2.jpg',
          isActive: true,
        ),
        const VideoStream(
          id: '3',
          title: 'Video Stream 3',
          streamUrl: '/app/logs/stream_3.jpg',
          isActive: true,
        ),
      ];
      emit(VideoStreamsLoaded(streams));
    });

    on<UpdateStreamStatusEvent>((event, emit) {
      final updatedStreams = state.streams.map((stream) {
        if (stream.id == event.streamId) {
          return stream.copyWith(
            isActive: event.isActive,
            lastUpdate: DateTime.now(),
            motionDetections: event.motionDetections,
          );
        }
        return stream;
      }).toList();

      emit(VideoStreamsLoaded(updatedStreams));
    });

    on<AddStreamEvent>((event, emit) {
      final updatedStreams = List<VideoStream>.of(state.streams)..add(event.stream);
      emit(VideoStreamsLoaded(updatedStreams));
    });

    on<RemoveStreamEvent>((event, emit) {
      final updatedStreams = state.streams.where((s) => s.id != event.streamId).toList();
      emit(VideoStreamsLoaded(updatedStreams));
    });

    on<StartRecordingEvent>((event, emit) async {
      // Create signal file to tell algorithm service to start recording
      final signalFile = File('/app/logs/record_start_${event.streamId}.signal');
      try {
        await signalFile.create();
      } catch (e) {
        print('Failed to create signal file: $e');
      }

      final updatedStreams = state.streams.map((stream) {
        if (stream.id == event.streamId) {
          return stream.copyWith(
            isRecording: true,
            recordingFilename: 'stream_${event.streamId}_recording.avi',
          );
        }
        return stream;
      }).toList();

      emit(VideoStreamsLoaded(updatedStreams));
    });

    on<StopRecordingEvent>((event, emit) async {
      // Create signal file to tell algorithm service to stop recording
      final signalFile = File('/app/logs/record_stop_${event.streamId}.signal');
      try {
        await signalFile.create();
      } catch (e) {
        print('Failed to create signal file: $e');
      }

      final updatedStreams = state.streams.map((stream) {
        if (stream.id == event.streamId) {
          return stream.copyWith(
            isRecording: false,
            recordingFilename: null,
          );
        }
        return stream;
      }).toList();

      emit(VideoStreamsLoaded(updatedStreams));
    });
  }
}
