# Audio Sample Extraction (Development)

Easily extract audio segments from YouTube videos for training data collection.

## Usage

### Basic Extraction

Extract a segment from a YouTube video by specifying the start and end times:

```bash
python youtube_audio_extractor.py "https://www.youtube.com/watch?v=VIDEO_ID" "1:30" "2:45"
```

### Custom Output Filename

Save the extracted audio with a custom filename:

```bash
python youtube_audio_extractor.py "https://youtu.be/VIDEO_ID" "0:15" "1:30" --output "accent_sample.wav"
```

## Arguments

- **URL**: The YouTube video link.
- **Start Time**: Segment start time (format: `MM:SS` or `HH:MM:SS`).
- **End Time**: Segment end time (format: `MM:SS` or `HH:MM:SS`).
- `--output`: (Optional) Custom output filename.

## Requirements

- Python 3.7+
- [pytube](https://pytube.io/) for downloading YouTube videos
- [pydub](https://github.com/jiaaro/pydub) for audio processing

Install dependencies:

```bash
pip install pytube pydub
```

## Example

Extract a 30-second sample and save as `sample.wav`:

```bash
python youtube_audio_extractor.py "https://www.youtube.com/watch?v=abcd1234" "0:00" "0:30" --output "sample.wav"
```

## Notes

- Output is in WAV format by default.
- Ensure `ffmpeg` is installed for audio conversion.
- Useful for collecting accent, pronunciation, or speech samples for ML training.

