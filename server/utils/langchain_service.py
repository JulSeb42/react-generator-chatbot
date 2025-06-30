"""LangChain service for React code generation and UI analysis.

This module provides AI-powered React code generation capabilities using OpenAI's GPT-4
and vision models, integrated with Pinecone vector database for context retrieval.

Classes:
    CustomPineconeRetriever: Custom retriever for Pinecone vector database integration
    ReactCodeAssistant: Main service class for React code generation and image analysis

Features:
    - Generate React/TypeScript components from text descriptions
    - Analyze UI mockup images using OpenAI Vision API
    - Retrieve relevant code examples from Pinecone vector database
    - Support for modern React patterns (hooks, functional components)
    - Tailwind CSS styling integration
    - TypeScript interface generation

Dependencies:
    - OpenAI API for code generation and vision analysis
    - Pinecone for vector similarity search
    - LangChain for prompt management and orchestration
    - LangSmith for tracing and monitoring

Usage:
    The module automatically creates a global `react_assistant` instance that can be
    imported and used throughout the application for AI-powered code generation.

Example:
    from utils.langchain_service import react_assistant

    # Generate React code from description
    code = react_assistant.generate_code("Create a button component")

    # Analyze UI mockup image
    description = react_assistant.analyze_image(base64_image_data)
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage, Document
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
from pinecone import Pinecone
from pinecone.exceptions import PineconeException
from utils.consts import PINECONE_API_KEY, OPENAI_API_KEY


class CustomPineconeRetriever:
    """Custom Pinecone retriever that works without langchain-pinecone"""

    def __init__(self, index, embeddings):
        self.index = index
        self.embeddings = embeddings

    def get_relevant_documents(self, query: str, k: int = 3):
        """Retrieve relevant documents from Pinecone based on semantic similarity.

        This method converts the input query to an embedding vector, searches the Pinecone
        index for the most similar documents, and returns them as LangChain Document objects.

        Args:
                query (str): The search query to find relevant documents for
                k (int, optional): Maximum number of documents to retrieve. Defaults to 3.

        Returns:
                list[Document]: List of LangChain Document objects containing:
                        - page_content: The text content from Pinecone metadata
                        - metadata: Additional metadata associated with the document

        Raises:
                Exception: If embedding generation or Pinecone query fails

        Example:
                retriever = CustomPineconeRetriever(index, embeddings)
                docs = retriever.get_relevant_documents("React button component", k=5)
                for doc in docs:
                        print(doc.page_content)
        """
        # Generate embedding for query
        query_embedding = self.embeddings.embed_query(query)

        # Search Pinecone
        results = self.index.query(
            vector=query_embedding, top_k=k, include_metadata=True
        )

        # Convert to LangChain documents
        documents = []
        for match in results.matches:
            doc = Document(
                page_content=match.metadata.get("text", ""), metadata=match.metadata
            )
            documents.append(doc)

        return documents

    def get_similar_scores(self, query: str, k: int = 3):
        """Get similarity scores along with documents.

        Args:
            query (str): The search query
            k (int, optional): Maximum number of results. Defaults to 3.

        Returns:
            list[tuple]: List of (Document, score) tuples
        """
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_embedding, top_k=k, include_metadata=True
        )

        documents_with_scores = []
        for match in results.matches:
            doc = Document(
                page_content=match.metadata.get("text", ""), metadata=match.metadata
            )
            documents_with_scores.append((doc, match.score))

        return documents_with_scores


class ReactCodeAssistant:
    """AI-powered React code generation assistant with vision capabilities.

    This class provides intelligent React component generation using OpenAI's GPT-4 model,
    enhanced with UI mockup analysis through vision AI and contextual code retrieval
    from a Pinecone vector database.

    The assistant specializes in creating modern React components with TypeScript support,
    Tailwind CSS styling, and follows current best practices including hooks, accessibility,
    and responsive design patterns.

    Attributes:
        llm (ChatOpenAI): Primary language model for code generation
        vision_llm (ChatOpenAI): Vision-enabled model for image analysis
        index (Pinecone.Index): Pinecone vector database index for code examples
        embeddings (OpenAIEmbeddings): OpenAI embeddings model for semantic search
        retriever (CustomPineconeRetriever): Custom retriever for relevant code context
        prompt_template (ChatPromptTemplate): Structured prompt template for code generation

    Features:
        - Generate functional React components with modern patterns
        - Analyze UI mockups and wireframes using computer vision
        - Retrieve contextually relevant code examples from vector database
        - Support TypeScript interfaces and type definitions
        - Implement Tailwind CSS styling automatically
        - Follow accessibility and responsive design principles
        - Provide complete, copy-paste ready code solutions

    Dependencies:
        - OpenAI API (GPT-4 and Vision models)
        - Pinecone vector database for code context
        - LangChain for prompt orchestration
        - LangSmith for performance tracing

    Example:
        # Generate a React component from text description
        assistant = ReactCodeAssistant()
        code = assistant.generate_code("Create a responsive login form with validation")

        # Analyze a UI mockup image
        description = assistant.analyze_image(base64_encoded_image)

        # Search for similar code patterns
        examples = assistant.search_similar_code("button component with hover effects")

    Raises:
        Exception: If OpenAI API credentials are invalid or missing
        ConnectionError: If Pinecone database connection fails
        TimeoutError: If API requests exceed configured timeout limits
    """

    def __init__(self):
        # Initialize LLMs with timeouts
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=OPENAI_API_KEY,
            timeout=45,
            max_retries=1,
        )

        # Initialize vision-enabled LLM
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=OPENAI_API_KEY,
            timeout=30,
            max_retries=1,
        )

        # Initialize Pinecone
        try:
            pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = pc.Index("ironhack-final-project")
            print("✅ Pinecone initialized")
        except PineconeException as e:
            print(f"❌ Pinecone service error: {e}")
            self.index = None
        except (ValueError, TypeError) as e:
            print(f"❌ Pinecone configuration error: {e}")
            self.index = None
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"❌ Unexpected Pinecone error: {e}")
            self.index = None

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", api_key=OPENAI_API_KEY
        )

        # Initialize custom retriever
        if self.index:
            self.retriever = CustomPineconeRetriever(self.index, self.embeddings)
        else:
            self.retriever = None

        # Create prompts
        self.system_prompt = """You are a senior React developer assistant. Generate high-quality React code based on user requests and UI mockups.

When creating React components:
- Use functional components with modern React hooks
- Include proper TypeScript interfaces when applicable
- Use Tailwind CSS for styling when possible
- Implement realistic functionality and event handlers
- Follow React best practices and patterns
- Make components responsive and accessible

Always provide complete, working code that can be copy-pasted and used immediately.

Here are some related React code examples for reference:
{context}

User request: {question}"""

        self.prompt_template = ChatPromptTemplate.from_template(self.system_prompt)
        print("✅ ReactCodeAssistant initialization complete")

    @traceable(run_type="chain", name="react_code_generation")
    def generate_code(self, user_input: str, image_description: str = None) -> str:
        """Generate React code based on user input and optional image description"""
        try:
            if image_description:
                combined_input = f"{user_input}\n\nUI Analysis: {image_description}"
            else:
                combined_input = user_input

            # Get relevant documents from Pinecone (with fallback)
            context = ""
            if self.retriever:
                try:
                    docs = self.retriever.get_relevant_documents(combined_input, k=2)
                    context = "\n\n".join([doc.page_content for doc in docs])
                    print(f"Retrieved context length: {len(context)} chars")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Retriever error (continuing without context): {e}")
                    context = "No context available"
            else:
                context = "No context available"

            # Create the prompt
            prompt = self.prompt_template.format(
                context=context, question=combined_input
            )

            # Generate response
            response = self.llm.invoke([HumanMessage(content=prompt)])

            return response.content

        except Exception as e:  # pylint: disable=broad-exception-caught
            return f"I apologize, but I encountered an error generating the code: {str(e)}. Please try with a simpler request."  # pylint: disable=line-too-long

    @traceable(run_type="llm", name="image_analysis")
    def analyze_image(self, base64_image: str) -> str:
        """Analyze UI mockup image and return description"""
        try:
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Analyze this UI mockup image and provide a detailed description for generating React code. Include layout, components, styling, colors, positioning, and component hierarchy. Be specific about the visual elements and their functionality.",  # pylint: disable=line-too-long
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ]
            )

            response = self.vision_llm.invoke([message])

            return response.content

        except Exception as e:
            print(f"❌ Vision API error: {str(e)}")
            raise e

    @traceable(run_type="retriever", name="similarity_search")
    def search_similar_code(self, query: str, k: int = 3):
        """Search for similar React code snippets"""
        if self.retriever:
            return self.retriever.get_relevant_documents(query, k)
        return []


# Create global instance
react_assistant = ReactCodeAssistant()
