from crewai import Agent, LLM
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from tools.pdf_tools import buscar_imagen_destino
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import os

llm = LLM(
    model="lm_studio/mistral-nemo-instruct-2407",
    base_url="http://127.0.0.1:1234/v1",
    api_key="lmstudio"
)

class ScientificAgents():

    def research_agent(self):
        return Agent(
            role='Scientific Researcher',
            goal='Research rigorous academic information and create a detailed structure for the scientific document',
            backstory="""You are an academic researcher with extensive experience in searching
            and analyzing scientific literature. Your specialty is finding reliable sources,
            analyzing complex information, and creating logical structures for academic documents.
            You have access to scientific databases and know how to evaluate source quality.
            
            IMPORTANT: You MUST provide complete, detailed research output. Never provide
            incomplete responses or just fragments. Always deliver comprehensive research
            findings with full structure, content summaries, and reference lists.""",
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website
            ],
            llm=llm,
            verbose=True,
            max_execution_time=600,  # 10 minutos
            allow_delegation=False
        )

    def writer_agent(self):
        return Agent(
            role='Scientific Writer',
            goal='Write comprehensive academic content based on the provided research',
            backstory="""You are a scientific writer specialized in academic communication.
            Your experience includes writing papers, review articles, and technical documents.
            You know how to present complex information clearly and structured,
            following international academic standards. Your style is precise, objective, and
            well-grounded in scientific evidence.
            
            IMPORTANT: You MUST write extensive, detailed content. Aim for comprehensive
            coverage of the topic with substantial paragraphs, detailed explanations,
            and thorough analysis. Never write short or superficial content.""",
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website
            ],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def structurer_agent(self):
        return Agent(
            role='Academic Document Structurer',
            goal='Organize and structure comprehensive document content with professional academic formatting',
            backstory="""You are an expert in academic document structuring with over
            15 years of experience in scientific editing. Your specialty is taking raw content
            and organizing it into professional documents that meet international
            academic standards. You perfectly know citation formats,
            scientific document structure, and how to present information clearly
            and professionally.
            
            IMPORTANT: You MUST create extensive, well-structured documents.
            Expand content where necessary, add detailed sections, and ensure
            the final document is comprehensive and substantial.
            
            CRITICAL: You ONLY output clean, academic content. You NEVER include
            meta-comments, process descriptions, or introductory statements about
            your work. You start directly with the document content.
            """,
            tools=[],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def image_specialist(self):
        return Agent(
            role='Scientific Image Specialist',
            goal='Find and download the perfect cover image for the scientific document',
            backstory="""You are a scientific image specialist with experience in
            selecting visual material for academic publications. Your expertise
            includes searching for high-quality images that represent scientific
            concepts professionally and attractively.""",
            tools=[buscar_imagen_destino],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
