"""
RAG Pipeline utilities for document loading, chunking, embedding, and retrieval
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGPipeline:
    def __init__(self, personality_id, documents_path, persist_directory="vector_store"):
        """
        Initialize RAG pipeline for a specific personality

        Args:
            personality_id: ID of the personality (e.g., 'steve_jobs')
            documents_path: Path to the document(s) to load
            persist_directory: Directory to persist vector store
        """
        self.personality_id = personality_id
        self.documents_path = documents_path
        self.persist_directory = os.path.join(persist_directory, personality_id)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None

    def load_documents(self):
        """Load documents from PDF"""
        print(f"Loading documents from {self.documents_path}...")
        loader = PyPDFLoader(self.documents_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages")
        return documents

    def split_documents(self, documents):
        """Split documents into chunks"""
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        return chunks

    def create_vectorstore(self, chunks):
        """Create and persist vector store"""
        print("Creating vector store with embeddings...")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore

    def load_vectorstore(self):
        """Load existing vector store"""
        print(f"Loading vector store from {self.persist_directory}...")
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        return self.vectorstore

    def get_retriever(self, k=4):
        """Get retriever from vector store"""
        if self.vectorstore is None:
            # Try to load existing vectorstore
            if os.path.exists(self.persist_directory):
                self.load_vectorstore()
            else:
                raise ValueError("Vector store not initialized. Run setup() first.")

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        return self.retriever

    def setup(self):
        """Complete setup: load, split, embed, and store documents"""
        # Check if vectorstore already exists
        if os.path.exists(self.persist_directory):
            print(f"Vector store already exists for {self.personality_id}")
            self.load_vectorstore()
        else:
            # Load and process documents
            documents = self.load_documents()
            chunks = self.split_documents(documents)
            self.create_vectorstore(chunks)

        # Create retriever
        self.get_retriever()
        print(f"RAG pipeline ready for {self.personality_id}")
        return self

    def query(self, question, system_prompt_template):
        """
        Query the RAG pipeline

        Args:
            question: User's question
            system_prompt_template: Template with {context} and {question} placeholders

        Returns:
            dict with 'response' and 'sources'
        """
        if self.retriever is None:
            self.get_retriever()

        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(question)

        # Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Format the prompt
        prompt = system_prompt_template.format(
            context=context,
            question=question
        )

        # Get LLM response
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        response = llm.invoke(prompt)

        # Format sources
        sources = []
        for i, doc in enumerate(relevant_docs):
            sources.append({
                "title": f"Stanford Commencement Speech - Page {doc.metadata.get('page', i+1)}",
                "excerpt": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "page": doc.metadata.get('page', i+1)
            })

        return {
            "response": response.content,
            "sources": sources
        }


def setup_personality_rag(personality_id, documents_path):
    """
    Helper function to set up RAG pipeline for a personality

    Args:
        personality_id: ID of the personality
        documents_path: Path to the document(s)

    Returns:
        RAGPipeline instance
    """
    pipeline = RAGPipeline(personality_id, documents_path)
    pipeline.setup()
    return pipeline


if __name__ == "__main__":
    # Test the pipeline
    print("Testing RAG Pipeline...")
    pipeline = setup_personality_rag(
        personality_id="steve_jobs",
        documents_path="steve_job_pdf.pdf"
    )

    test_question = "How do I know if my product idea is good enough?"
    result = pipeline.query(
        test_question,
        "Context: {context}\n\nQuestion: {question}\n\nAnswer as Steve Jobs:"
    )

    print("\n" + "="*50)
    print(f"Question: {test_question}")
    print("="*50)
    print(f"Answer: {result['answer']}")
    print("\n" + "="*50)
    print("Sources:")
    for source in result['sources']:
        print(f"- {source['title']}: {source['excerpt']}")
