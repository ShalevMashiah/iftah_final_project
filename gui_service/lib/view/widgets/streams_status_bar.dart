import 'package:flutter/material.dart';

/// Status bar showing stream statistics
class StreamsStatusBar extends StatelessWidget {
  final int totalStreams;
  final int activeStreams;
  final int inactiveStreams;

  const StreamsStatusBar({
    super.key,
    required this.totalStreams,
    required this.activeStreams,
    required this.inactiveStreams,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      color: const Color(0xFF1E1E1E),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _StatusItem(
            label: 'Total Streams',
            value: totalStreams.toString(),
            color: Colors.blue,
          ),
          _StatusItem(
            label: 'Active',
            value: activeStreams.toString(),
            color: Colors.green,
          ),
          _StatusItem(
            label: 'Inactive',
            value: inactiveStreams.toString(),
            color: Colors.red,
          ),
        ],
      ),
    );
  }
}

class _StatusItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatusItem({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(Icons.circle, color: color, size: 12),
        const SizedBox(width: 8),
        Text(
          '$label: $value',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
