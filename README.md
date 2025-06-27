# React Code Generator AI

An AI-powered React component generation service that creates React components from text descriptions and UI mockup images using OpenAI's GPT-4 and Vision models, enhanced with vector similarity search.

**Created by [Julien Sebag](https://julien-sebag.com/) for the Ironhack AI Bootcamp Final Project**

## 🚀 Features

- **AI-Powered Code Generation**: Generate React components from natural language descriptions
- **UI Mockup Analysis**: Upload images of UI mockups and get corresponding React code
- **Smart Context Retrieval**: Vector similarity search for relevant code examples
- **Real-time Chat Interface**: Interactive conversation-based development workflow
- **Image Upload & Processing**: Drag & drop image support with Cloudinary integration
- **Session Management**: Persistent conversation history across sessions
- **Knowledge Base Population**: Automated dataset ingestion from HuggingFace

## 🛠 Tech Stack

### Backend (Python/Flask)
- **Flask** - Web framework
- **OpenAI GPT-4** - Code generation and vision analysis
- **Pinecone** - Vector database for similarity search
- **MongoDB** - Message and session storage
- **Cloudinary** - Image hosting and processing
- **LangChain** - AI orchestration and prompt management
- **LangSmith** - AI operation monitoring

### Frontend (React/TypeScript)
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Toastify** - Notifications

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **MongoDB** (local or Atlas)
- **API Keys** for:
  - OpenAI
  - Pinecone
  - Cloudinary

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd react-generator-chatbot
```

### 2. Backend Setup
```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd client

# Install dependencies
npm install
# or
yarn install
```

### 4. Environment Configuration

Create `.env` files in both `server/` and `client/` directories:

**Server `.env`:**
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
MONGODB_URI=mongodb://localhost:27017/react-code-generator
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
CLIENT_URI=http://localhost:5173
TOKEN_SECRET=your_jwt_secret
LANGCHAIN_PROJECT=react-code-generator
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=your_langsmith_api_key
```

**Client `.env`:**
```env
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Running the Application

### Start the Backend Server
```bash
cd server

# Option 1: Direct Python execution
python app.py

# Option 2: Using Flask CLI
flask --app app run --port=8000 --reload

# Option 3: Using Gunicorn (production)
gunicorn app:app --bind 0.0.0.0:8000
```

Server will be available at: `http://localhost:8000`

### Start the Frontend Development Server
```bash
cd client

# Using npm
npm run dev

# Using yarn
yarn dev
```

Frontend will be available at: `http://localhost:5173`

## 📊 Initial Setup & Data Population

### 1. Initialize Pinecone Index
```bash
cd server
python utils/populate_pinecone.py
```

### 2. Populate Knowledge Base from HuggingFace
```bash
curl -X POST http://localhost:8000/api/populate/populate-from-hf
```

## 🔗 API Endpoints

### Chat & Code Generation
- `POST /api/chat/new-chat` - Generate React code from text/image
- `GET /api/chat/messages/<session_id>` - Get conversation history
- `DELETE /api/chat/delete-session/<session_id>` - Delete session
- `POST /api/chat/upload-image` - Upload UI mockup images

### Knowledge Base Management
- `POST /api/chat/add-snippet` - Add code snippet to knowledge base
- `POST /api/populate/populate-from-hf` - Import HuggingFace dataset

### Health & Monitoring
- `GET /api/` - Basic health check
- `GET /api/health` - Detailed server status

## 💡 Usage Examples

### Generate React Component from Description
```bash
curl -X POST http://localhost:8000/api/chat/new-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a responsive login form with email validation",
    "session_id": "unique-session-id"
  }'
```

### Upload UI Mockup Image
```bash
curl -X POST http://localhost:8000/api/chat/upload-image \
  -F "image=@path/to/mockup.png"
```

### Generate Code from Image
```bash
curl -X POST http://localhost:8000/api/chat/new-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate React code for this UI",
    "image_url": "https://res.cloudinary.com/your-cloud/image.jpg",
    "session_id": "unique-session-id"
  }'
```

## 🏗 Project Structure

```
final-project/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── types/          # TypeScript types
│   │   ├── utils/          # Utility functions
│   │   └── main.tsx        # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── server/                 # Flask backend
│   ├── routes/             # API route blueprints
│   │   ├── chat.py         # Chat & code generation
│   │   └── populate_from_hf.py  # Dataset population
│   ├── utils/              # Utility modules
│   │   ├── langchain_service.py  # AI orchestration
│   │   ├── cloudinary_service.py # Image handling
│   │   ├── connect_db.py   # Database connection
│   │   └── populate_pinecone.py  # Vector DB setup
│   ├── app.py              # Flask application
│   └── requirements.txt
│
└── README.md
```

## 🔒 Security Considerations

- API keys stored in environment variables
- Input validation for all user data
- File type validation for image uploads
- Session isolation for user conversations
- CORS configuration for frontend integration

## 📈 Performance Optimizations

- Vector similarity search for relevant code context
- Batch processing for dataset population
- Image optimization via Cloudinary
- Connection pooling for database operations
- Caching for frequently requested code patterns

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
- Check Python version (3.8+ required)
- Verify all environment variables are set
- Ensure MongoDB is running
- Check API key validity

**Frontend not connecting:**
- Verify backend is running on port 8000
- Check CORS configuration
- Validate environment variables

**Image upload failing:**
- Check Cloudinary credentials
- Verify file size limits (5MB max)
- Ensure supported file types (PNG, JPG, GIF)

**Vector search not working:**
- Run Pinecone initialization script
- Check Pinecone API key and index name
- Verify embeddings are being generated

## 👨‍💻 Author

**Julien Sebag**
- Portfolio: [julien-sebag.com](https://julien-sebag.com/)
- Project: Ironhack AI Bootcamp React Chatbot

## 📝 License

MIT License

Copyright (c) 2025 Julien Sebag

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions about this project, please contact [Julien Sebag](mailto:julien.sebag@me.com) or refer to the React Chatbot documentation.

---

**Built with ❤️ by [Julien Sebag](https://julien-sebag.com/) for the Ironhack AI Bootcamp Final Project**