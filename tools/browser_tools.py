import json
import os
import requests
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai_tools import ScrapeWebsiteTool

class BrowserTools():

    @tool("Scrape website content")
    def scrape_and_summarize_website(website: str) -> str:
        """Useful to scrape and summarize a website content"""
        
        try:
            # Crear instancia de ScrapeWebsiteTool con la URL específica
            scrape_tool = ScrapeWebsiteTool(website_url=website)
            
            # Extraer el contenido del sitio web
            content = scrape_tool.run()
            
            if not content:
                return "No se pudo extraer contenido del sitio web."
            
            # Dividir el contenido en chunks para procesar
            chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]
            
            llm = LLM(
                model = "lm_studio/mistral-nemo-instruct-2407",
                base_url="http://127.0.0.1:1234/v1",
                api_key="lmstudio"
            )
            
            summaries = []
            
            for chunk in chunks:
                agent = Agent(
                    role='Principal Researcher',
                    goal='Generate summaries from long content',
                    backstory="Expert in distilling information.",
                    llm=llm,
                    allow_delegation=False
                )
                
                task = Task(
                    agent=agent,
                    description=f"Summarize the following content:\n\n{chunk}",
                    expected_output="A clean and informative summary of the content."
                )
                
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    verbose=False
                )
                
                summary = crew.kickoff()
                summaries.append(str(summary))
            
            return "\n\n".join(summaries)
            
        except Exception as e:
            print(f"Error al hacer scraping del sitio web {website}: {str(e)}")
            return f"Error al procesar el sitio web: {str(e)}"
