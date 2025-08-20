#!/usr/bin/env python3
"""
Supadata YouTube Transcriber

A script to fetch transcripts from YouTube videos using the Supadata library.
This script automatically processes URLs from youtube_url.csv and tracks completed/failed URLs.

Note: You need a Supadata API key to use this script.
Get your API key from: https://supadata.ai/
"""

import sys
import re
import os
import csv
import time
from typing import Optional, List, Tuple
from dotenv import load_dotenv
from supadata import Supadata, SupadataError


def load_environment():
    """Load environment variables from .env file."""
    # Load .env file if it exists
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('SUPADATA_API_KEY')
    
    if not api_key:
        print("Error: SUPADATA_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("SUPADATA_API_KEY=your_actual_api_key_here")
        print("\nOr set the environment variable:")
        print("export SUPADATA_API_KEY=your_actual_api_key_here")
        sys.exit(1)
    
    return api_key


def ensure_transcripts_folder():
    """Ensure the transcripts folder exists."""
    transcripts_dir = "transcripts"
    try:
        if not os.path.exists(transcripts_dir):
            os.makedirs(transcripts_dir, exist_ok=True)
            print(f"Created transcripts folder: {transcripts_dir}")
        else:
            print(f"Using existing transcripts folder: {transcripts_dir}")
        return transcripts_dir
    except Exception as e:
        print(f"Error creating transcripts folder: {e}")
        # Try to create in current directory as fallback
        fallback_dir = "transcripts_fallback"
        try:
            os.makedirs(fallback_dir, exist_ok=True)
            print(f"Created fallback folder: {fallback_dir}")
            return fallback_dir
        except Exception as fallback_e:
            print(f"Critical error: Could not create any transcripts folder: {fallback_e}")
            raise


def load_completed_urls() -> set:
    """Load already completed YouTube URLs from file."""
    completed_file = "youtube_url_completed.txt"
    completed_urls = set()
    
    if os.path.exists(completed_file):
        try:
            with open(completed_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url:
                        completed_urls.add(url)
            print(f"Loaded {len(completed_urls)} completed URLs from {completed_file}")
        except Exception as e:
            print(f"Warning: Could not load completed URLs: {e}")
    
    return completed_urls


def load_failed_urls() -> set:
    """Load failed YouTube URLs from file."""
    failed_file = "youtube_url_failed.txt"
    failed_urls = set()
    
    if os.path.exists(failed_file):
        try:
            with open(failed_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # Split by tab to separate URL from reason
                    parts = line.strip().split('\t')
                    url = parts[0] if parts else ""
                    if url:
                        failed_urls.add(url)
            print(f"Loaded {len(failed_urls)} failed URLs from {failed_file}")
        except Exception as e:
            print(f"Warning: Could not load failed URLs: {e}")
    
    return failed_urls


def save_completed_url(url: str) -> None:
    """Save a completed YouTube URL to the tracking file."""
    completed_file = "youtube_url_completed.txt"
    
    try:
        with open(completed_file, 'a', encoding='utf-8') as f:
            f.write(f"{url}\n")
        print(f"Saved completed URL: {url}")
    except Exception as e:
        print(f"Warning: Could not save completed URL: {e}")


def save_failed_url(url: str, reason: str = "Unknown error") -> None:
    """Save a failed YouTube URL to the tracking file with reason."""
    failed_file = "youtube_url_failed.txt"
    
    try:
        with open(failed_file, 'a', encoding='utf-8') as f:
            f.write(f"{url}\t{reason}\n")
        print(f"Saved failed URL: {url} - Reason: {reason}")
    except Exception as e:
        print(f"Warning: Could not save failed URL: {e}")


def read_csv_urls(csv_file: str = "youtube_url.csv") -> List[Tuple[str, str, str]]:
    """
    Read YouTube URLs from CSV file.
    
    Args:
        csv_file (str): Path to CSV file
        
    Returns:
        List[Tuple[str, str, str]]: List of (video_id, url, description) tuples
    """
    urls = []
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return urls
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, 1):
                if len(row) >= 2:
                    video_id = row[0].strip('"')
                    url = row[1].strip('"')
                    description = row[2].strip('"') if len(row) > 2 else ""
                    urls.append((video_id, url, description))
                else:
                    print(f"Warning: Row {row_num} has insufficient columns: {row}")
        
        print(f"Loaded {len(urls)} URLs from CSV file")
        return urls
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return urls


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url (str): YouTube URL (supports various formats)
        
    Returns:
        Optional[str]: Video ID if found, None otherwise
    """
    # Handle various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_transcript(url: str, video_id: str, description: str, language: str = 'en') -> bool:
    """
    Get transcript from a YouTube video using Supadata.
    """
    try:
        # Load API key from environment
        api_key = load_environment()
        
        # Ensure transcripts folder exists
        transcripts_dir = ensure_transcripts_folder()
        
        # Initialize Supadata client
        client = Supadata(api_key=api_key)
        
        print(f"\n{'='*60}")
        print(f"Processing: {description}")
        print(f"URL: {url}")
        print(f"Video ID: {video_id}")
        print(f"Language: {language}")
        print(f"{'='*60}")
        
        # Get transcript directly (no metadata needed)
        print("\nFetching transcript...")
        try:
            # Get transcript in plain text format
            transcript = client.youtube.transcript(url, lang=language, text=True)
            
            print("Transcript retrieved successfully!")
            
            # Save transcript to file in transcripts folder with simplified filename
            filename = os.path.join(transcripts_dir, f"{video_id}.txt")
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write header with video information
                    f.write(f"Video ID: {video_id}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Description: {description}\n")
                    f.write(f"Language: {language}\n")
                    f.write("-" * 50 + "\n\n")
                    
                    # Write transcript content
                    f.write(transcript.content if hasattr(transcript, 'content') else str(transcript))
                
                print(f"Transcript saved to: {filename}")
                
                # Mark as completed
                save_completed_url(url)
                return True
                
            except Exception as e:
                error_msg = f"File save error: {e}"
                print(f"Error saving transcript to file: {e}")
                save_failed_url(url, error_msg)
                return False
                
        except SupadataError as e:
            error_msg = f"Supadata API error: {e}"
            print(f"Supadata API error: {e}")
            print("This might be due to:")
            print("- Invalid API key")
            print("- API rate limits")
            print("- Video not having transcripts")
            print("- Language not available")
            save_failed_url(url, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Transcript fetch error: {e}"
            print(f"Error getting transcript: {e}")
            save_failed_url(url, error_msg)
            return False
            
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"Unexpected error: {e}")
        save_failed_url(url, error_msg)
        return False


def process_csv_urls(csv_file: str = "youtube_url.csv", language: str = 'en') -> None:
    """
    Process all URLs from CSV file and fetch transcripts.
    
    Args:
        csv_file (str): Path to CSV file
        language (str): Language code for transcripts
        """
    # Ensure transcripts folder exists before starting processing
    try:
        transcripts_dir = ensure_transcripts_folder()
        print(f"Transcripts will be saved to: {transcripts_dir}")
    except Exception as e:
        print(f"Critical error: Cannot proceed without transcripts folder: {e}")
        return
    
    # Load URLs from CSV
    urls = read_csv_urls(csv_file)
    if not urls:
        print("No URLs found in CSV file")
        return
    
    # Load already completed and failed URLs
    completed_urls = load_completed_urls()
    failed_urls = load_failed_urls()
    
    # Filter out already completed and failed URLs
    pending_urls = [(video_id, url, description) for video_id, url, description in urls 
                    if url not in completed_urls and url not in failed_urls]
    
    if not pending_urls:
        print("All URLs have already been processed (completed or failed)!")
        return
    
    print(f"Found {len(pending_urls)} URLs to process (out of {len(urls)} total)")
    print(f"Already completed: {len(completed_urls)}")
    print(f"Previously failed: {len(failed_urls)}")
    
    # Process each URL
    successful = 0
    failed = 0
    
    for i, (video_id, url, description) in enumerate(pending_urls, 1):
        print(f"\nProcessing {i}/{len(pending_urls)}: {description}")
        
        if get_youtube_transcript(url, video_id, description, language):
            successful += 1
        else:
            failed += 1
        
        # Add 5-second pause after each URL to avoid API rate limits
        if i < len(pending_urls):  # Don't pause after the last URL
            print(f"\nPausing for 5 seconds before next URL...")
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total URLs in CSV: {len(urls)}")
    print(f"Already completed: {len(completed_urls)}")
    print(f"Previously failed: {len(failed_urls)}")
    print(f"Processed this run: {len(pending_urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Transcripts saved to: transcripts/ folder")
    print(f"Failed URLs saved to: youtube_url_failed.txt")


def main():
    """Main function to handle command line usage."""
    # Parse options
    language = 'en'
    
    for i, arg in enumerate(sys.argv):
        if arg == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
        elif arg == '--help' or arg == '-h':
            print("Usage: python3 youtube_transcript_supadata.py [options]")
            print("\nOptions:")
            print("  --language <lang>     Language code (e.g., 'en', 'es', 'fr') - defaults to 'en'")

            print("  --help, -h            Show this help message")
            print("\nExamples:")
            print("  python3 youtube_transcript_supadata.py")
            print("  python3 youtube_transcript_supadata.py --language es")
            print("\nEnvironment Setup:")
            print("  1. Create a .env file with: SUPADATA_API_KEY=your_api_key_here")
            print("  2. Or set environment variable: export SUPADATA_API_KEY=your_api_key_here")
            print("  3. Get your API key from: https://supadata.ai/")
            print("\nNote: The script automatically processes youtube_url.csv")
            print("Default format: Plain text")
            print("Rate limiting: 5-second pause between URLs to avoid API limits")
            sys.exit(0)
    
    # Always process the CSV file by default
    print("YouTube Transcript Fetcher - Processing youtube_url.csv")
    print("=" * 60)
    
    # Ensure transcripts folder exists before starting
    try:
        ensure_transcripts_folder()
    except Exception as e:
        print(f"Critical error: Cannot create transcripts folder: {e}")
        print("Please check permissions and try again.")
        sys.exit(1)
    
    process_csv_urls(language=language)


if __name__ == "__main__":
    main()
