# Castify Server

Castify is a service that converts PDF documents into podcast-style audio conversations. The application extracts text from PDFs, processes it using RAG (Retrieval-Augmented Generation), generates a conversational script using Gemini AI, and synthesizes natural-sounding audio using ElevenLabs voice technology.

## Features

- PDF text extraction with metadata support
- RAG-based content processing for improved context understanding
- AI-powered conversation generation with Google's Gemini API
- High-quality text-to-speech conversion with ElevenLabs
- Two-speaker audio synthesis for natural podcast-like conversations
- RESTful API for integration with other applications
- Background task processing for handling large documents
- Simple web interface for manual uploads

## Installation

### Prerequisites

- Python 3.10+
- FFmpeg (required for audio processing)
- Google Gemini API key
- ElevenLabs API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/castify-server.git
   cd castify-server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create an `.env` file with your API keys (see Environment Configuration section)

5. Create required directories:
   ```bash
   mkdir -p uploads outputs
   ```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```dotenv
# Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Application Settings
DEBUG=True  # Set to False in production
HOST=0.0.0.0
PORT=5000

# Voices Configuration
VOICE_S1=JBFqnCBsd6RMkjVDRZzb  # Rachel voice ID
VOICE_S2=EXAVITQu4vr4xnSDxMaL  # Adam voice ID
```

## Usage

### Running the Server

Start the server:
```bash
python src/server.py
```

The web interface will be available at http://localhost:5000

### Converting a PDF

1. Upload a PDF through the web interface at http://localhost:5000
2. Optionally provide a custom prompt to guide the conversation style
3. Wait for the processing to complete (this may take some time depending on document length)
4. Access the generated podcast audio file through the provided URL

## API Endpoints

### Upload PDF
- **URL**: `/upload`
- **Method**: `POST`
- **Form Data**:
  - `file`: PDF file (required)
  - `prompt`: Custom prompt (optional)
- **Response**: JSON with task ID and status URL

### Check Task Status
- **URL**: `/status/<task_id>`
- **Method**: `GET`
- **Response**: JSON with task status and result (when complete)

### Get Audio
- **URL**: `/audio/<filename>`
- **Method**: `GET`
- **Response**: Audio file (MP3)

### List Tasks
- **URL**: `/tasks`
- **Method**: `GET`
- **Response**: JSON with all tasks and their statuses

### List Outputs
- **URL**: `/outputs`
- **Method**: `GET`
- **Response**: JSON with list of generated audio files

## Docker Deployment

Build and run the Docker container:
```bash
# Build the image
docker build -t castify-server .

# Run the container
docker run -p 5000:5000 castify-server
```

## Project Structure

```
castify-server/
├── .env                # Environment configuration
├── Dockerfile          # Docker configuration
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── src/                # Source code
│   ├── main.py         # Core processing logic
│   ├── server.py       # Flask web server
│   ├── pdf_parser/     # PDF extraction modules
│   ├── rag_system/     # RAG processing modules
│   ├── gemini_api/     # Gemini API client
│   ├── eli/            # ElevenLabs API client
│   └── output/         # Output generation modules
├── uploads/            # Uploaded PDF storage
└── outputs/            # Generated audio storage
```

## Notes

- Large PDF files may take longer to process
- The quality of the generated conversation depends on the clarity and structure of the input document
- Default voices can be changed by updating the voice IDs in the .env file

## License

[Specify your license here]
