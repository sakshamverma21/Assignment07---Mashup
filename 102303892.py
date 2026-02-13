#!/usr/bin/env python3
"""
Mashup Program - Downloads YouTube videos of a singer, converts to audio,
cuts first Y seconds, and merges into a single output file.

Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>
Example: python mashup.py "Sharry Maan" 20 20 output.mp3
"""

import sys
import os
from pytubefix import YouTube, Search
from pydub import AudioSegment
import shutil

# Configure ffmpeg and ffprobe paths for pydub
ffmpeg_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                           'Microsoft', 'WinGet', 'Packages',
                           'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
                           'ffmpeg-8.0.1-full_build', 'bin', 'ffmpeg.exe')
ffprobe_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                            'Microsoft', 'WinGet', 'Packages',
                            'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
                            'ffmpeg-8.0.1-full_build', 'bin', 'ffprobe.exe')
if os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path


def validate_arguments(args):
    """Validate command line arguments"""
    if len(args) != 5:
        print("Error: Incorrect number of parameters")
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print("Example: python mashup.py 'Sharry Maan' 20 20 output.mp3")
        sys.exit(1)
    
    singer_name = args[1]
    
    try:
        num_videos = int(args[2])
        if num_videos <= 10:
            print("Error: Number of videos must be greater than 10")
            sys.exit(1)
    except ValueError:
        print("Error: Number of videos must be a valid integer")
        sys.exit(1)
    
    try:
        duration = int(args[3])
        if duration <= 20:
            print("Error: Audio duration must be greater than 20 seconds")
            sys.exit(1)
    except ValueError:
        print("Error: Audio duration must be a valid integer")
        sys.exit(1)
    
    output_file = args[4]
    if not output_file.endswith(('.mp3', '.mp4')):
        print("Warning: Output file should have .mp3 or .mp4 extension")
    
    return singer_name, num_videos, duration, output_file


def download_videos(singer_name, num_videos):
    """Download videos from YouTube"""
    print(f"\nSearching for '{singer_name}' videos on YouTube...")
    
    # Create temporary directory for downloads
    temp_dir = "temp_downloads"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Search for videos
        search = Search(singer_name)
        results = search.results
        
        if not results:
            print(f"Error: No search results found for '{singer_name}'")
            print("Suggestions:")
            print("- Try a more common or different spelling")
            print("- Check your internet connection")
            print("- Try a different singer name")
            sys.exit(1)
        
        if len(results) < num_videos:
            print(f"Warning: Only {len(results)} videos found for '{singer_name}'")
            print(f"Will download all {len(results)} available videos")
        
        downloaded_files = []
        
        for i, video in enumerate(results[:num_videos]):
            try:
                print(f"Downloading video {i+1}/{min(num_videos, len(results))}: {video.title[:50]}...")
                
                # Download audio stream
                audio_stream = video.streams.filter(only_audio=True).first()
                if audio_stream:
                    output_path = audio_stream.download(
                        output_path=temp_dir,
                        filename=f"video_{i}.mp4"
                    )
                    downloaded_files.append(output_path)
                    print(f"✓ Successfully downloaded video {i+1}")
                else:
                    print(f"Warning: No audio stream found for video {i+1}")
                    
            except Exception as e:
                print(f"Error downloading video {i+1}: {str(e)}")
                continue
        
        if len(downloaded_files) == 0:
            print("\nError: No videos were successfully downloaded")
            print("This can happen if:")
            print("1. The singer name returned no valid results")
            print("2. All videos failed to download (network issues)")
            print("3. YouTube API restrictions")
            print("4. Special characters in the name caused issues")
            print("\nTry:")
            print("- Using a more common spelling")
            print("- Removing special characters from the name")
            print("- Checking your internet connection")
            sys.exit(1)
        
        print(f"\nSuccessfully downloaded {len(downloaded_files)} videos")
        return downloaded_files
        
    except Exception as e:
        print(f"Error during video download: {str(e)}")
        sys.exit(1)


def convert_to_audio(video_files):
    """Convert video files to audio format"""
    print("\nProcessing audio from videos...")
    audio_files = []
    
    for i, video_file in enumerate(video_files):
        try:
            print(f"Processing file {i+1}/{len(video_files)}...")
            audio = AudioSegment.from_file(video_file)
            audio_file = video_file.replace('.mp4', '_audio.mp4')
            audio.export(audio_file, format='mp4', codec='aac')
            audio_files.append(audio_file)
        except Exception as e:
            print(f"Error processing audio {i+1}: {str(e)}")
            continue
    
    print(f"Successfully processed {len(audio_files)} audio files")
    return audio_files


def cut_audio(audio_files, duration):
    """Cut first Y seconds from each audio file"""
    print(f"\nCutting first {duration} seconds from each audio...")
    cut_audio_files = []
    
    for i, audio_file in enumerate(audio_files):
        try:
            audio = AudioSegment.from_file(audio_file)
            
            # Cut first 'duration' seconds (duration is in seconds, pydub uses milliseconds)
            cut_audio = audio[:duration * 1000]
            
            cut_file = audio_file.replace('_audio.mp4', '_cut.mp4')
            cut_audio.export(cut_file, format='mp4', codec='aac')
            cut_audio_files.append(cut_file)
            
        except Exception as e:
            print(f"Error cutting audio {i+1}: {str(e)}")
            continue
    
    print(f"Successfully cut {len(cut_audio_files)} audio files")
    return cut_audio_files


def merge_audio(audio_files, output_file):
    """Merge all audio files into a single output file"""
    print("\nMerging audio files...")
    
    try:
        # Start with empty audio
        combined = AudioSegment.empty()
        
        for i, audio_file in enumerate(audio_files):
            audio = AudioSegment.from_file(audio_file)
            combined += audio
            print(f"Merged file {i+1}/{len(audio_files)}")
        
        # Export final merged file as MP4
        combined.export(
            output_file,
            format='mp4',
            codec='aac',
            bitrate='192k'
        )
        print(f"\nSuccess! Mashup created: {output_file}")
        print(f"Total duration: {len(combined)/1000:.2f} seconds")
        
    except Exception as e:
        print(f"Error merging audio files: {str(e)}")
        sys.exit(1)


def cleanup(temp_dir="temp_downloads"):
    """Clean up temporary files"""
    print("\nCleaning up temporary files...")
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("Cleanup complete")
    except Exception as e:
        print(f"Warning: Could not clean up temporary files: {str(e)}")


def main():
    """Main function"""
    print("=" * 60)
    print("YouTube Mashup Generator")
    print("=" * 60)
    
    # Validate arguments
    singer_name, num_videos, duration, output_file = validate_arguments(sys.argv)
    
    try:
        # Download videos
        video_files = download_videos(singer_name, num_videos)
        
        # Convert to audio
        audio_files = convert_to_audio(video_files)
        
        # Cut audio
        cut_files = cut_audio(audio_files, duration)
        
        # Merge audio
        merge_audio(cut_files, output_file)
        
        # Cleanup
        cleanup()
        
        print("\n" + "=" * 60)
        print("Mashup generation completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
