#!/usr/bin/env python3
"""
Example usage of YouTube Audio Extractor for Speaklarity project
"""

from Speaklarity.test_dir.youtube_audio_extractor import YouTubeAudioExtractor

def main():
    # Create extractor instance
    extractor = YouTubeAudioExtractor(output_dir="training_samples")
    
    # Example URLs with different accents for testing
    sample_extractions = [
        {
            "url": "https://www.youtube.com/watch?v=example1",
            "start_time": "1:30",
            "end_time": "2:15",
            "description": "British accent sample"
        },
        {
            "url": "https://www.youtube.com/watch?v=example2", 
            "start_time": "0:45",
            "end_time": "1:30",
            "description": "American accent sample"
        },
        # Add your actual YouTube URLs here
    ]
    
    print("🎬 Speaklarity Audio Sample Extractor")
    print("=" * 40)
    
    for i, sample in enumerate(sample_extractions, 1):
        print(f"\n📝 Extracting sample {i}: {sample['description']}")
        
        result = extractor.extract_audio_segment(
            youtube_url=sample['url'],
            start_time=sample['start_time'],
            end_time=sample['end_time'],
            output_filename=f"sample_{i:02d}_{sample['description'].lower().replace(' ', '_')}.wav"
        )
        
        if result:
            print(f"✅ Successfully extracted: {result}")
        else:
            print(f"❌ Failed to extract sample {i}")

if __name__ == "__main__":
    main()
