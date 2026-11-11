from crewai import Task
from textwrap import dedent

class ScientificTasks:

    def research_task(self, agent, topic, pages):
        return Task(
            description=dedent(f"""
            Conduct comprehensive research on the topic: {topic}

            Your task includes:
            1. Search for current and relevant academic information on the topic
            2. Identify the most reliable and recent sources (preferably last 5 years)
            3. Create a detailed structure for a {pages} document
            4. Identify the most important subtopics to cover
            5. Collect data, statistics, and scientific evidence
            6. Find at least 8-12 valid academic references

            The document should have the following basic structure:
            - Introduction
            - 3-4 main development sections
            - Conclusions
            - References

            {self.__tip_section()}

            Topic: {topic}
            Length: {pages}
            """),
            agent=agent,
            expected_output="""A detailed research report that includes:
            - Proposed document structure with sections and subsections
            - Summary of key findings for each section
            - List of academic references found with URLs when possible
            - Relevant data and statistics
            - Key concepts that should be explained"""
        )

    def writing_task(self, agent, research_output, topic):
        return Task(
            description=dedent(f"""
            Based on the provided research, write the complete content
            of the scientific document on: {topic}

            Available research information:
            {research_output}

            Your task includes:
            1. Write an introduction that contextualizes the topic
            2. Develop each main section with substantial content
            3. Include clear explanations of technical concepts
            4. Integrate data and statistics naturally
            5. Maintain an academic but accessible tone
            6. Ensure coherence and flow between sections
            7. Include practical examples when appropriate

            Format requirements:
            - Use level 2 headings (##) for main sections
            - Use level 3 headings (###) for subsections
            - Include well-structured paragraphs
            - Integrate citations from found sources

            {self.__tip_section()}
            """),
            agent=agent,
            expected_output="""Complete scientific document in Markdown format that includes:
            - Comprehensive introduction (1-2 paragraphs)
            - 3-4 well-developed main sections
            - Conclusions that synthesize key points
            - Precise but accessible technical content
            - Appropriate length for the requested format"""
        )

    def structuring_task(self, agent, content, topic):
        return Task(
            description=dedent(f"""
            Take the written content and structure it into a final professional
            academic document on: {topic}

            Content to structure:
            {content}

            Your task includes:
            1. Organize content with professional academic formatting
            2. Create a comprehensive references section with proper formatting
            3. Ensure the structure is logical and coherent
            4. Add formatting elements that improve readability
            5. Format citations and references correctly

            IMPORTANT INSTRUCTIONS:
            - NEVER include meta-comments about the document creation process
            - NEVER mention "comprehensive document", "final answer", or similar phrases
            - NEVER include word counts or formatting instructions
            - NEVER add introductory comments about the task
            - ONLY provide the clean, academic content
            - Start directly with the document title and content

            Required final structure:
            - Main sections using # headers
            - Subsections using ## headers
            - Sub-subsections using ### headers
            - Introduction
            - Content sections and subsections
            - Conclusions
            - References section

            OUTPUT ONLY THE CLEAN EXTENSE ACADEMIC DOCUMENT - NO META-COMMENTS, NO TABLE OF CONTENTS, NO FORMULAS, NO INTRO TEXT, JUST THE CLEAN ACADEMIC DOCUMENT FOLLOWING THE REQUIRED FINAL STRUCTURE.

            {self.__tip_section()}
            """),
            agent=agent,
            expected_output="""Clean scientific document in Markdown format with:
            - Professional academic content ONLY
            - NO meta-comments or process descriptions
            - NO introductory agent statements
            - Direct start with document title and content
            - Proper academic structure and formatting
            - Well-formatted references section"""
        )

    def image_task(self, agent, topic):
        return Task(
            description=dedent(f"""
            Search and download a high-quality image to use as cover
            for the scientific document on: {topic}

            The image should be:
            - Professional and academic
            - Representative of the scientific topic
            - High resolution and visual quality
            - Appropriate for an academic document
            - Without obvious watermarks

            Topic: {topic}
            Use the provided tool.

            {self.__tip_section()}
            """),
            agent=agent,
            expected_output="Confirmation that an appropriate image has been successfully downloaded for the document cover"
        )

    def __tip_section(self):
        return "If you do your BEST WORK, you will receive a $100 tip!"
