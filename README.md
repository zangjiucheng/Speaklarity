# SPEAKLARITY

**SPEAKLARITY** is an innovative AI-powered accent correction and pronunciation improvement platform that transforms audio recordings into personalized feedback sessions. Built upon state-of-the-art speech recognition technologies, including insights from OpenAI's Whisper model, our system leverages robust speech processing capabilities to provide accurate accent analysis across multiple languages and dialects. Whether you're a language learner looking to improve your accent or a professional aiming to enhance your communication skills, our intelligent system analyzes speech patterns, identifies pronunciation issues, and provides real-time corrections to help you speak clearly and confidently.

## Features

- **Real-time Audio Recording & Analysis** - Record your speech directly in the browser with live audio visualization
- **AI-Powered Accent Detection** - Advanced algorithms identify accent patterns and pronunciation discrepancies
- **Grammar & Pronunciation Checking** - Comprehensive analysis of both grammatical accuracy and spoken clarity
- **Interactive Speech Feedback** - Visual and textual feedback to guide pronunciation improvements
- **Progress Tracking** - Monitor your improvement over time with detailed analytics
- **Modern Web Interface** - Beautiful, responsive React TypeScript frontend with animations
- **YouTube Audio Extraction** - Tools for extracting training samples from YouTube videos for testing

## Installation

(Developed on Windows 11, Python 3.11+ environment, Node.js 18+)

### Clone the repository:

```bash
git clone https://github.com/zangjiucheng/Speaklarity.git
cd Speaklarity
```

### Backend Setup:

```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
# Windows (using winget):
winget install ffmpeg
# Or download from https://ffmpeg.org/download.html
```

### Frontend Setup:

```bash
cd frontend
npm install
cd ..
```

## Usage

### Running the Application

1. **Start the Backend server:**
```bash
cd backend
python app.py
```

2. **Start the Frontend development server:**
```bash
cd frontend
npm run dev
```

3. **Access the web application** at `http://localhost:5173`

### Using the Application

1. **Navigate to the main application** from the landing page
2. **Click "New Recording"** to start a speech analysis session
3. **Grant microphone permissions** when prompted
4. **Press the record button** to start recording your speech
5. **Press again to stop** recording and automatically upload for analysis
6. **View your analysis results** and receive personalized feedback

## API Endpoints

- `POST /upload-conversation`: Upload audio file for accent and grammar analysis
- `GET /analysis/<id>`: Retrieve analysis results for a specific recording
- `GET /progress/<id>`: Check processing status ("pending", "processing", "completed")
- `POST /feedback/<id>`: Submit user feedback on analysis accuracy

## Project Structure

```
Speaklarity/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── Main/            # Main application pages
│   │   ├── utils/           # API utilities and types
│   │   └── (root)/          # Landing page
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                 # Python backend (planned)
│   ├── accent_check.py      # Accent analysis logic
│   ├── grammar_check.py     # Grammar checking
│   ├── process.py           # Main processing pipeline
│   └── route.py             # API routes
├── youtube_audio_extractor.py # Audio extraction utility
└── requirements.txt         # Python dependencies
```

## Technology Stack

**Frontend:**
- React 19 with TypeScript
- Vite (build tool)
- Tailwind CSS + HeroUI (styling)
- Framer Motion (animations)
- React Router (routing)

**Backend:**
- Python 3.11+
- Audio processing libraries
- AI/ML models for accent analysis

**Tools:**
- FFmpeg (audio processing)
- yt-dlp (YouTube audio extraction)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## References & Acknowledgements

### Research & Algorithms

Our speech processing and accent analysis capabilities are built upon cutting-edge research in robust speech recognition and large-scale audio processing:

- **Whisper Speech Recognition**: Our platform leverages insights from OpenAI's Whisper model, which demonstrates exceptional performance in multilingual speech recognition through large-scale weak supervision training on 680,000 hours of diverse audio data.
- Advanced speech processing techniques for accent analysis and pronunciation assessment
- Natural language processing algorithms for grammar checking and linguistic pattern recognition
- Real-time audio visualization and processing algorithms

### Key Research References

- Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022). *Robust Speech Recognition via Large-Scale Weak Supervision*. arXiv preprint arXiv:2212.04356. [Read the paper](https://arxiv.org/abs/2212.04356)

### Third-Party Libraries

**Frontend:**
- [HeroUI](https://heroui.com/) - Modern React component library
- [Framer Motion](https://www.framer.com/motion/) - Animation library
- [React Hot Toast](https://react-hot-toast.com/) - Notification system

**Backend:**
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube audio extraction
- [pydub](https://github.com/jiaaro/pydub) - Audio manipulation
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing

---

**Built with ❤️ for clearer communication and confident speaking.**
