#!/usr/bin/env python3
"""
YouTube Audio Extractor for Speaklarity Hackathon Project
Extracts audio segments from YouTube videos in WAV format
"""

import os
import sys
import argparse
from pathlib import Path
import yt_dlp
from pydub import AudioSegment
import tempfile
import shutil

class YouTubeAudioExtractor:
    def __init__(self, output_dir="audio_samples"):
        """
        Initialize the YouTube Audio Extractor
        
        Args:
            output_dir (str): Directory to save extracted audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_audio_segment(self, youtube_url, start_time, end_time, output_filename=None):
        """
        Extract audio segment from YouTube video
        
        Args:
            youtube_url (str): YouTube video URL
            start_time (str): Start time in format "MM:SS" or "HH:MM:SS"
            end_time (str): End time in format "MM:SS" or "HH:MM:SS"
            output_filename (str, optional): Custom filename for output WAV file
            
        Returns:
            str: Path to the extracted WAV file
        """
        try:
            # Convert time strings to seconds
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            if start_seconds >= end_seconds:
                raise ValueError("Start time must be before end time")
            
            print(f"Extracting audio from {youtube_url}")
            print(f"Time range: {start_time} to {end_time}")
            
            # Create temporary directory for intermediate files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Configure yt-dlp options for audio extraction
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(temp_path / 'temp_audio.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                }
                
                # Download and extract audio
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                    video_title = info.get('title', 'Unknown')
                    video_id = info.get('id', 'unknown')
                
                # Find the downloaded audio file
                audio_file = None
                for file in temp_path.glob('temp_audio.*'):
                    if file.suffix.lower() in ['.wav', '.mp3', '.m4a', '.webm']:
                        audio_file = file
                        break
                
                if not audio_file:
                    raise FileNotFoundError("Downloaded audio file not found")
                
                print(f"Processing audio: {video_title}")
                
                # Load audio with pydub
                audio = AudioSegment.from_file(str(audio_file))
                
                # Extract the specified segment (pydub works in milliseconds)
                start_ms = start_seconds * 1000
                end_ms = end_seconds * 1000
                
                if end_ms > len(audio):
                    print(f"Warning: End time ({end_time}) exceeds video duration. Adjusting to video end.")
                    end_ms = len(audio)
                
                audio_segment = audio[start_ms:end_ms]
                
                # Generate output filename if not provided
                if not output_filename:
                    safe_title = self._sanitize_filename(video_title)
                    output_filename = f"{safe_title}_{video_id}_{start_time.replace(':', '')}-{end_time.replace(':', '')}.wav"
                
                # Ensure .wav extension
                if not output_filename.endswith('.wav'):
                    output_filename += '.wav'
                
                # Save the audio segment
                output_path = self.output_dir / output_filename
                audio_segment.export(str(output_path), format="wav")
                
                print(f"✅ Audio extracted successfully!")
                print(f"📁 Saved to: {output_path}")
                print(f"⏱️  Duration: {len(audio_segment) / 1000:.2f} seconds")
                
                return str(output_path)
                
        except Exception as e:
            print(f"❌ Error extracting audio: {str(e)}")
            return None
    
    def _time_to_seconds(self, time_str):
        """Convert time string (MM:SS or HH:MM:SS) to seconds"""
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            raise ValueError(f"Invalid time format: {time_str}. Use MM:SS or HH:MM:SS")
    
    def _sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:50]  # Limit length

def main():
    parser = argparse.ArgumentParser(
        description='Extract audio segments from YouTube videos for accent analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python youtube_audio_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "1:30" "2:45"
  python youtube_audio_extractor.py "https://youtu.be/dQw4w9WgXcQ" "0:15" "1:30" --output "british_accent_sample.wav"
  python youtube_audio_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "2:15" "3:00" --dir "training_data"
        """
    )
    
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('start_time', help='Start time (MM:SS or HH:MM:SS)')
    parser.add_argument('end_time', help='End time (MM:SS or HH:MM:SS)')
    parser.add_argument('--output', '-o', help='Output filename (optional)')
    parser.add_argument('--dir', '-d', default='audio_samples', help='Output directory (default: audio_samples)')
    
    args = parser.parse_args()
    
    # Create extractor instance
    extractor = YouTubeAudioExtractor(output_dir=args.dir)
    
    # Extract audio segment
    result = extractor.extract_audio_segment(
        youtube_url=args.url,
        start_time=args.start_time,
        end_time=args.end_time,
        output_filename=args.output
    )
    
    if result:
        print(f"\n🎉 Success! Audio saved to: {result}")
        return 0
    else:
        print(f"\n💥 Failed to extract audio")
        return 1

if __name__ == "__main__":
    sys.exit(main())
