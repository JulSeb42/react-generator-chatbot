from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage, Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langsmith import traceable
from pinecone import Pinecone
from utils.consts import PINECONE_API_KEY, OPENAI_API_KEY


class CustomPineconeRetriever:
    """Custom Pinecone retriever that works without langchain-pinecone"""

    def __init__(self, index, embeddings):
        self.index = index
        self.embeddings = embeddings

    def get_relevant_documents(self, query: str, k: int = 3):
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


class ReactCodeAssistant:
    def __init__(self):
        # Initialize LLMs with timeouts (FIXED - removed duplicate)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=OPENAI_API_KEY,
            timeout=45,  # Increased timeout
            max_retries=1,
        )

        # Initialize vision-enabled LLM
        self.vision_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=OPENAI_API_KEY,
            timeout=30,  # Shorter timeout for vision
            max_retries=1,
        )

        # Initialize Pinecone
        try:
            pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = pc.Index("ironhack-final-project")
        except Exception as e:
            print(f"❌ Pinecone error: {e}")
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
                    docs = self.retriever.get_relevant_documents(
                        combined_input, k=2
                    )  # Reduced k
                    context = "\n\n".join([doc.page_content for doc in docs])
                    print(f"Retrieved context length: {len(context)} chars")
                except Exception as e:
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

        except Exception as e:
            return f"I apologize, but I encountered an error generating the code: {str(e)}. Please try with a simpler request."

    @traceable(run_type="llm", name="image_analysis")
    def analyze_image(self, base64_image: str) -> str:
        """Analyze UI mockup image and return description"""
        try:
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Analyze this UI mockup image and provide a detailed description for generating React code. Include layout, components, styling, colors, positioning, and component hierarchy. Be specific about the visual elements and their functionality.",
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
        else:
            return []


# Create global instance
react_assistant = ReactCodeAssistant()
