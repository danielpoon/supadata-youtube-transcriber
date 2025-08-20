# Supadata YouTube Transcriber

Version 1.0

By Daniel Poon

Git Repo: [danielpoon/supadata-youtube-transcriber · GitHub](https://github.com/danielpoon/supadata-youtube-transcriber.git)

After creating the [gemini-youtube-ai-transcriber](https://github.com/danielpoon/gemini-youtube-ai-transcriber), there appear to be a limitation of context token of 1M where video that's over 45 minutes could not be processed without spliting videos into parts. This Python script was written to provide an alternative via the Supadata library:

1. The script will pull transcripts of YouTube but it will not provide other functionalities that AI can e.g. a summary or key points

2. The speed is less than 30 seconds each, which is faster than Gemini API although ig time stamping is important, I haven't had success in getting timestamps along side the transcription.

3. Cater for pulling multiple YouTube URLs

4. Not all YouTube URLs will work ~10-15% failure but the failed URLs are tracked so you could perhaps use AI to work on those

5. Supadata provides free tier of 100 credits (1 credit = 1 transcript)  and also a $9 tier for 1,000 credits (at time of writing).

## Prerequisites

- Python 3.9+
- Supadata API key (get from [https://supadata.ai/](https://supadata.ai/))

## Installation

1. Install the required dependencies:
   
   ```bash
   pip3 install -r requirements.txt
   ```

2. Get your Supadata API key from [https://supadata.ai/](https://supadata.ai/)

3. Set up your API key (choose one method):
   
   **Option A: Using .env file (Recommended)**
   
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key
   SUPADATA_API_KEY=your_actual_api_key_here
   ```
   
   **Option B: Using environment variable**
   
   ```bash
   export SUPADATA_API_KEY=your_actual_api_key_here
   ```

## Usage

### Simple CSV Processing (Recommended)

The script automatically processes all YouTube URLs from `youtube_url.csv`:

```bash
# Process all URLs from youtube_url.csv (default: segments with timestamps)
python3 youtube_transcript_supadata.py

# Process with specific language
python3 youtube_transcript_supadata.py --language es

# Show help
python3 youtube_transcript_supadata.py --help
```

**CSV Format**: The script expects `youtube_url.csv` with columns:

- Column 1: YouTube Video ID
- Column 2: YouTube URL  
- Column 3: Description (optional)

**Example CSV**:

```csv
"OBG50aoUwlI","https://www.youtube.com/watch?v=OBG50aoUwlI","NYU's 2022 Commencement Speaker Taylor Swift"
```

#### Arguments:

- `--language <lang>`: Language code (e.g., 'en', 'es', 'fr') - optional, defaults to 'en'
- `--help, -h`: Show help message

**Default Behavior**: The script outputs **plain text** transcripts by default for simplicity.

## Progress Tracking

The script automatically tracks URLs in multiple tracking files:

### **Completed URLs** (`youtube_url_completed.txt`)

- **Resume capability**: If interrupted, restart and skip already processed URLs
- **Progress monitoring**: See how many URLs are pending vs. completed
- **Efficient processing**: Only process new URLs on subsequent runs

### **Failed URLs** (`youtube_url_failed.txt`)

- **Error logging**: Records URLs that failed with specific error reasons
- **Skip failed URLs**: Automatically skips previously failed URLs on restart
- **Error analysis**: Review failed URLs to understand common issues
- **Retry capability**: Manually remove failed URLs to retry processing

**Failed URL Format**:

```
https://www.youtube.com/watch?v=example1    Supadata API error: No transcript available
https://www.youtube.com/watch?v=example2    File save error: Permission denied
```

## Output

The script will:

1. **Automatically create `transcripts/` folder** if it doesn't exist
2. Show processing progress and status for each URL
3. **Save transcripts to `transcripts/` folder with simplified filenames** (e.g., `transcripts/3wddoD1e4M0.txt`)
4. **Track completed URLs** in `youtube_url_completed.txt`
5. **Track failed URLs** in `youtube_url_failed.txt` with error reasons
6. Display comprehensive summary of processing results

### Folder Management

The script includes robust folder management:

- **Automatic creation**: Creates `transcripts/` folder if missing
- **Permission checking**: Verifies write access before processing
- **Fallback handling**: Creates alternative folder if primary fails
- **Error reporting**: Clear messages about folder status

**Note**: The script focuses on transcript retrieval only, avoiding unnecessary API calls for video metadata to minimize costs.

### Sample Transcript Content

Here's what the actual transcript output looks like from your current video:

```
Video ID: OBG50aoUwlI
URL: https://www.youtube.com/watch?v=OBG50aoUwlI
Description: NYU's 2022 Commencement Speaker Taylor Swift
Language: en
--------------------------------------------------

(audience clapping) - I would like now to introduce Jason King Chair and Associate Professor of the Clive Davis Institute of Recorded Music, Tisch School of the Arts, who will present the candidate for Doctor of Fine Arts. Will trustee, Brett Racon, please escort the candidate to the lectern. (audience applauding)

(audience cheering) - Taylor Swift (audience cheering) (audience applauding) blazing singer, songwriter, producer, director, actress, pioneering and influential advocate for artists' rights and philanthropist. You have brought joy and resolve to your hundreds of millions of fans throughout the world. (audience cheering) One of the best selling music artists in history...

[Transcript continues with full commencement speech content]
```

### Rate Limiting

The script includes built-in rate limiting to be respectful to the Supadata API:

- **5-second pause** between processing each URL
- **Prevents API rate limit errors** during batch processing
- **Configurable**: Can be adjusted in the code if needed
- **Progress indicator**: Shows pause countdown during processing

### Transcript File Format

Each transcript file includes a header with:

```
Video ID: OBG50aoUwlI
URL: https://www.youtube.com/watch?v=OBG50aoUwlI
Description: NYU's 2022 Commencement Speaker Taylor Swift
Language: en
--------------------------------------------------

(audience clapping) - I would like now to introduce Jason King Chair and Associate Professor of the Clive Davis
Institute of Recorded Music, Tisch School of the Arts, who will present the candidate
for Doctor of Fine Arts. Will trustee, Brett Racon, please escort the
candidate to the lectern. (audience applauding)
...
```

## File Organization

```
youtube-transcribe-bulk/
|-- transcripts/                           # Transcript files folder
|   |-- OBG50aoUwlI.txt                  # Example transcript file
|   |-- [other transcript files...]
|-- youtube_url.csv                       # Input CSV with YouTube URLs
|-- youtube_url_completed.txt             # Tracking file for completed URLs
|-- youtube_url_failed.txt                # Tracking file for failed URLs
|-- youtube_transcript_supadata.py        # Main script (simplified usage)
|-- requirements.txt                      # Python dependencies
|-- .env.example                         # Environment variables template
|-- README.md                            # This file## Environment Variables

```

The following environment variables can be configured in your `.env` file:

- `SUPADATA_API_KEY`: Your Supadata API key (required)
- `DEFAULT_LANGUAGE`: Default language for transcripts (optional, defaults to 'en')
- `DEFAULT_OUTPUT_FORMAT`: Default output format (optional, defaults to 'plain_text')

## Dependencies

- `supadata`: Official Python SDK for Supadata
- `python-dotenv`: Environment variable management
- Standard Python libraries (re, sys, typing, os, csv, time, etc.)

**Note**: Only 2 external packages are required. All other imports are part of Python's standard library.

## Troubleshooting

### Common Issues

1. **"SUPADATA_API_KEY not found" error**: 
   
   - Make sure you have a `.env` file with your API key
   - Or set the environment variable: `export SUPADATA_API_KEY=your_key`

2. **"No URLs found in CSV file"**: 
   
   - Check that `youtube_url.csv` exists and has the correct format
   - Ensure CSV has at least 2 columns (Video ID and URL)

3. **"No transcripts available"**: The video may not have transcripts enabled

4. **"Language not available"**: Try using a different language code or check available languages

5. **Rate limiting**: The API may have rate limits - wait and try again

### Failed URL

Review `youtube_url_failed.txt` to understand common failure reasons:

- **"No transcript available"**: Video doesn't have transcripts enabled
- **"API rate limit"**: Too many requests, wait and retry
- **"File save error"**: Permission or disk space issues
- **"Network error"**: Connection problems, retry later

### Getting Help

- Check the [Supadata documentation](https://supadata.ai/)
- Ensure your API key is valid and has sufficient credits
- Verify the YouTube video has transcripts enabled

## Security Notes

- **Never commit your `.env` file** to version control
- The `.env.example` file is safe to commit (contains no real API keys)
- Use environment variables for sensitive information in production

## License

This project is for educational and personal use. Please respect YouTube's terms of service and Supadata's API usage policies.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the scripts.
