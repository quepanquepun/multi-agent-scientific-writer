import streamlit as st
from crewai import Crew, Flow
from crewai.flow.flow import listen, start
from scientific_agents import ScientificAgents
from scientific_tasks import ScientificTasks
from dotenv import load_dotenv
import os
import base64
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import re

load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Scientific Document Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_llm_info_from_agents():
    """Obtiene información del LLM desde la configuración de agentes"""
    try:
        agents = ScientificAgents()
        research_agent = agents.research_agent()
        llm_config = research_agent.llm
        
        return {
            "model": getattr(llm_config, 'model', 'Unknown'),
            "base_url": getattr(llm_config, 'base_url', 'Unknown'),
            "provider": "Local" if "127.0.0.1" in str(getattr(llm_config, 'base_url', '')) else "External API"
        }
    except Exception as e:
        return {
            "model": "Configuration Error",
            "base_url": "Check agents configuration",
            "provider": "Unknown"
        }

def convertir_imagen_a_base64(image_path: str) -> str:
    """Convierte imagen a base64 para embeber en HTML"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.gif'):
            mime_type = 'image/gif'
        else:
            mime_type = 'image/jpeg'
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        return ""

def generate_subtitle(topic: str) -> str:
    """Genera un subtítulo original basado en el tema"""
    subtitles = {
        "artificial intelligence": "Transforming Healthcare Through Innovation",
        "machine learning": "Advanced Computational Methods and Applications",
        "streptococcus": "Pathogenesis, Diagnosis and Clinical Management",
        "cancer": "Current Research and Therapeutic Approaches",
        "diabetes": "Molecular Mechanisms and Treatment Strategies",
        "covid": "Pandemic Response and Medical Advances",
        "genetics": "Molecular Biology and Clinical Applications",
        "neuroscience": "Brain Function and Neurological Disorders",
        "immunology": "Immune System Mechanisms and Therapeutics",
        "cardiology": "Cardiovascular Health and Disease Management"
    }
    
    topic_lower = topic.lower()
    for key, subtitle in subtitles.items():
        if key in topic_lower:
            return subtitle
    
    # Subtítulo genérico si no encuentra coincidencia
    return "Scientific Review and New Perspectives"

def limpiar_primer_ultimo_parrafo(contenido_markdown: str) -> str:
    """Elimina comentarios de agentes SOLO del primer y último párrafo si los detecta"""
    
    # Dividir en párrafos y filtrar vacíos
    paragrafos = [p.strip() for p in contenido_markdown.split('\n\n') if p.strip()]
    
    if not paragrafos:
        return contenido_markdown
    
    # Patrones específicos para comentarios de agentes
    patrones_comentarios = [
        r'^i understand the task.*?markdown format',
        r'^here\'s my final answer',
        r'^this comprehensive.*?document.*?provides',
        r'^this document.*?formatted for.*?pdf',
        r'^.*length of approximately.*?pages',
        r'^.*logically structured.*?professionally formatted',
        r'^let me provide.*?comprehensive',
        r'^based on.*?research.*?here.*?is',
        r'^i will provide.*?well-structured'
    ]
    
    # Verificar SOLO el primer párrafo
    if len(paragrafos) > 0:
        primer_parrafo = paragrafos[0].lower()
        es_comentario_primero = any(re.search(patron, primer_parrafo, re.DOTALL | re.IGNORECASE) 
                                   for patron in patrones_comentarios)
        
        if es_comentario_primero:
            paragrafos = paragrafos[1:]  # Eliminar primer párrafo
            print("🧹 Eliminado comentario de agente del primer párrafo")
    
    # Verificar SOLO el último párrafo (si hay más de uno)
    if len(paragrafos) > 1:
        ultimo_parrafo = paragrafos[-1].lower()
        es_comentario_ultimo = any(re.search(patron, ultimo_parrafo, re.DOTALL | re.IGNORECASE) 
                                  for patron in patrones_comentarios)
        
        if es_comentario_ultimo:
            paragrafos = paragrafos[:-1]  # Eliminar último párrafo
            print("🧹 Eliminado comentario de agente del último párrafo")
    
    return '\n\n'.join(paragrafos)

def generar_pdf_desde_markdown(contenido_markdown: str, titulo: str) -> str:
    """Genera PDF desde contenido markdown con diseño académico elegante"""
    try:
        if not os.path.exists("output"):
            os.makedirs("output")

        # Buscar imagen de portada
        imagen_base64 = ""
        for ext in ['.jpg', '.png', '.jpeg']:
            temp_image = os.path.join("temp", f"cover_image{ext}")
            if os.path.exists(temp_image):
                imagen_base64 = convertir_imagen_a_base64(temp_image)
                break

        # Convertir título a mayúsculas
        titulo_mayusculas = titulo.upper()
        
        # Generar subtítulo original
        subtitulo = generate_subtitle(titulo)

        # LIMPIAR SOLO PRIMER Y ÚLTIMO PÁRRAFO
        contenido_limpio = limpiar_primer_ultimo_parrafo(contenido_markdown)
        
        # Limpiezas adicionales menores
        contenido_limpio = re.sub(r'\n\s*\n\s*\n', '\n\n', contenido_limpio)  # Múltiples líneas vacías
        contenido_limpio = contenido_limpio.strip()  # Espacios al inicio y final

        # Convertir Markdown a HTML
        html_content_body = markdown.markdown(
            contenido_limpio, 
            extensions=['tables', 'fenced_code']
        )

        # Extraer TODOS los headers para TOC funcional con IDs únicos
        lines = contenido_limpio.split('\n')
        toc_items = []
        content_with_ids = []
        header_counter = 1
        
        for line in lines:
            # Headers # (nivel 1)
            if line.startswith('# ') and not line.startswith('## '):
                section_title = re.sub(r'[#*]', '', line).strip()
                if section_title and section_title not in ['Abstract', 'Table of Contents']:
                    header_id = f"main-section-{header_counter}"
                    toc_items.append(f'<li class="toc-level1"><a href="#{header_id}">{section_title}</a></li>')
                    content_with_ids.append(f'<h1 id="{header_id}">{section_title}</h1>')
                    header_counter += 1
                else:
                    content_with_ids.append(line)
            # Headers ## (nivel 2)
            elif line.startswith('## ') and not line.startswith('### '):
                section_title = re.sub(r'[#*]', '', line).strip()
                if section_title and section_title not in ['Abstract', 'Table of Contents', 'References']:
                    header_id = f"section-{header_counter}"
                    toc_items.append(f'<li class="toc-main"><a href="#{header_id}">{section_title}</a></li>')
                    content_with_ids.append(f'<h2 id="{header_id}">{section_title}</h2>')
                    header_counter += 1
                else:
                    content_with_ids.append(line)
            # Headers ### (nivel 3)
            elif line.startswith('### '):
                subsection_title = re.sub(r'[#*]', '', line).strip()
                if subsection_title:
                    header_id = f"subsection-{header_counter}"
                    toc_items.append(f'<li class="toc-sub"><a href="#{header_id}">{subsection_title}</a></li>')
                    content_with_ids.append(f'<h3 id="{header_id}">{subsection_title}</h3>')
                    header_counter += 1
            else:
                content_with_ids.append(line)

        # Regenerar HTML con IDs
        content_with_ids_markdown = '\n'.join(content_with_ids)
        html_content_body = markdown.markdown(
            content_with_ids_markdown, 
            extensions=['tables', 'fenced_code']
        )

        # TOC COMPACTO - ESTRUCTURA CORREGIDA
        toc_html = f"""
        <div class="toc-page">
            <h2 class="toc-title">Table of Contents</h2>
            <ul class="toc-list">
                {''.join(toc_items)}
            </ul>
        </div>
        """

        # HTML completo con CSS COMPLETAMENTE CORREGIDO
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{titulo_mayusculas}</title>
            <style>
                /* Página por defecto CON números */
                @page {{
                    size: A4;
                    margin: 3cm 2.5cm 4cm 2.5cm;
                    @bottom-center {{
                        content: "Page " counter(page);
                        font-family: 'Times New Roman', serif;
                        font-size: 10pt;
                        color: #666;
                        margin-bottom: 1cm;
                    }}
                }}
                
                /* Página de portada SIN números */
                @page :first {{
                    @bottom-center {{
                        content: '';
                    }}
                }}
                
                body {{
                    font-family: 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #2c3e50;
                    margin: 0;
                    padding: 0;
                }}
                
                /* PORTADA COMPACTA */
                .cover {{
                    text-align: center;
                    page-break-after: always;
                    padding: 1.5cm 2cm;
                    min-height: 80vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    align-items: center;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                }}
                
                .cover h1 {{
                    font-size: 28pt;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 0.8cm;
                    margin-top: 1cm;
                    line-height: 1.1;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    letter-spacing: 1px;
                }}
                
                .cover-subtitle {{
                    font-size: 16pt;
                    color: #34495e;
                    margin-bottom: 1.5cm;
                    font-style: italic;
                    font-weight: 300;
                }}
                
                .cover-image {{
                    max-width: 350px;
                    max-height: 200px;
                    width: auto;
                    height: auto;
                    margin: 0 auto 1.5cm auto;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                    display: block;
                    object-fit: contain;
                }}
                
                .cover-footer {{
                    margin-top: auto;
                    font-size: 12pt;
                    color: #7f8c8d;
                    font-weight: 300;
                }}
                
                /* TOC COMPACTO - DEFINITIVAMENTE CORREGIDO */
                .toc-page {{
                    page-break-after: always;
                    page-break-inside: avoid !important;
                    padding: 1.5cm 0;
                    display: block;
                }}
                
                .toc-title {{
                    color: #2c3e50;
                    font-size: 20pt;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin: 0 0 1cm 0;
                    text-align: center;
                    page-break-after: avoid !important;
                    page-break-inside: avoid !important;
                }}
                
                .toc-list {{
                    list-style: none;
                    padding-left: 0;
                    margin: 0;
                    page-break-inside: avoid !important;
                    display: block;
                }}
                
                /* Elementos TOC compactos */
                .toc-level1 {{
                    font-weight: bold;
                    margin: 4px 0;
                    padding: 3px 0;
                    border-bottom: 1px solid #3498db;
                    font-size: 12pt;
                    display: block;
                    page-break-inside: avoid !important;
                    color: #2c3e50;
                }}
                
                .toc-level1 a {{
                    text-decoration: none;
                    color: #2c3e50;
                    font-weight: bold;
                    display: block;
                }}
                
                .toc-level1 a:hover {{
                    color: #3498db;
                }}
                
                .toc-main {{
                    font-weight: bold;
                    margin: 3px 0 3px 15px;
                    padding: 2px 0;
                    border-bottom: 1px dotted #bdc3c7;
                    font-size: 11pt;
                    display: block;
                    page-break-inside: avoid !important;
                }}
                
                .toc-main a {{
                    text-decoration: none;
                    color: #2c3e50;
                    display: block;
                }}
                
                .toc-main a:hover {{
                    color: #3498db;
                }}
                
                .toc-sub {{
                    margin: 2px 0 2px 30px;
                    color: #7f8c8d;
                    font-size: 10pt;
                    display: block;
                    page-break-inside: avoid !important;
                }}
                
                .toc-sub a {{
                    text-decoration: none;
                    color: #7f8c8d;
                    display: block;
                }}
                
                .toc-sub a:hover {{
                    color: #3498db;
                }}
                
                /* Contenido principal */
                .content {{
                    margin-bottom: 2cm;
                }}
                
                h1 {{
                    color: #2c3e50;
                    font-size: 26pt;
                    margin: 40px 0 20px 0;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 15px;
                    page-break-before: always;
                }}
                
                h2 {{
                    color: #34495e;
                    font-size: 20pt;
                    margin: 35px 0 20px 0;
                    border-left: 5px solid #3498db;
                    padding-left: 20px;
                    page-break-inside: avoid;
                }}
                
                h3 {{
                    color: #5d6d7e;
                    font-size: 16pt;
                    margin: 25px 0 15px 0;
                    page-break-inside: avoid;
                }}
                
                /* TEXTO JUSTIFICADO - CORREGIDO */
                p {{
                    text-align: justify !important;
                    margin-bottom: 15px;
                    text-indent: 20px;
                    page-break-inside: avoid;
                    orphans: 3;
                    widows: 3;
                }}
                
                ul, ol {{
                    margin: 15px 0;
                    padding-left: 30px;
                    text-align: justify !important;
                }}
                
                li {{
                    margin-bottom: 8px;
                    text-align: justify !important;
                }}
                
                strong {{
                    color: #2c3e50;
                }}
                
                /* Referencias */
                .references {{
                    margin-top: 30px;
                }}
                
                .references h2 {{
                    border-left: 5px solid #e74c3c;
                }}
                
                .references p {{
                    text-indent: 0;
                    margin-left: 20px;
                    font-size: 11pt;
                    hanging-indent: 20px;
                    text-align: justify !important;
                }}
                
                /* Enlaces */
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <!-- Portada optimizada -->
            <div class="cover">
                <h1>{titulo_mayusculas}</h1>
                <div class="cover-subtitle">{subtitulo}</div>
                {f'<img src="{imagen_base64}" class="cover-image" alt="Cover Image">' if imagen_base64 else ''}
                <div class="cover-footer">
                    <p><strong>Generated:</strong> {st.session_state.get('fecha_actual', 'June 2025')}</p>
                </div>
            </div>
            
            <!-- Tabla de contenidos COMPACTA Y UNIFICADA -->
            {toc_html}
            
            <!-- Contenido principal -->
            <div class="content">
                {html_content_body}
            </div>
        </body>
        </html>
        """

        # Generar PDF
        filename = f"output/{titulo.replace(' ', '_')}.pdf"
        HTML(string=html_template).write_pdf(filename)
        
        return filename

    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None




class ScientificDocumentFlow(Flow):
    """Flow for generating scientific documents"""
    
    def __init__(self):
        super().__init__()
        self.agents = ScientificAgents()
        self.tasks = ScientificTasks()

    @start()
    def research_phase(self):
        st.info("🔍 Research phase...")
        research_agent = self.agents.research_agent()
        research_task = self.tasks.research_task(research_agent, st.session_state.topic, "3-5 pages")
        crew = Crew(agents=[research_agent], tasks=[research_task], verbose=False)
        return crew.kickoff()

    @listen(research_phase)
    def writing_phase(self, research_output):
        st.info("✍️ Writing phase...")
        writer_agent = self.agents.writer_agent()
        writing_task = self.tasks.writing_task(writer_agent, research_output, st.session_state.topic)
        crew = Crew(agents=[writer_agent], tasks=[writing_task], verbose=False)
        return crew.kickoff()

    @listen(writing_phase)
    def image_phase(self, writing_output):
        st.info("🖼️ Searching cover image...")
        image_agent = self.agents.image_specialist()
        image_task = self.tasks.image_task(image_agent, st.session_state.topic)
        crew = Crew(agents=[image_agent], tasks=[image_task], verbose=False)
        crew.kickoff()
        return writing_output

    @listen(image_phase)
    def structuring_phase(self, content):
        st.info("📋 Structuring document...")
        structurer_agent = self.agents.structurer_agent()
        structuring_task = self.tasks.structuring_task(structurer_agent, content, st.session_state.topic)
        crew = Crew(agents=[structurer_agent], tasks=[structuring_task], verbose=False)
        return crew.kickoff()

def main():
    # Interfaz simplificada
    st.title("🔬 Scientific Document Generator")
    
    # Sidebar desplegable con información del sistema
    with st.sidebar:
        st.header("⚙️ System Info")
        
        with st.expander("🤖 LLM Configuration", expanded=False):
            llm_info = get_llm_info_from_agents()
            st.write(f"**Model:** {llm_info['model']}")
            st.write(f"**Provider:** {llm_info['provider']}")
            if llm_info['provider'] == "Local":
                st.write(f"**URL:** {llm_info['base_url']}")
        
        with st.expander("👥 Agent Structure", expanded=False):
            agents_info = {
                "🔍 Research Agent": "Searches academic information",
                "✍️ Writing Agent": "Writes scientific content", 
                "🖼️ Image Specialist": "Finds cover images",
                "📋 Structurer": "Organizes final document"
            }
            for agent, desc in agents_info.items():
                st.write(f"**{agent}**")
                st.caption(desc)
        
        with st.expander("🔄 Workflow", expanded=False):
            st.write("1. Research → 2. Writing → 3. Image → 4. Structure → 5. PDF")

    # Interfaz principal ultra-simple
    st.markdown("### Generate your scientific document")
    
    # Solo input del tema
    topic = st.text_input(
        "**Enter your research topic:**",
        placeholder="e.g., Artificial Intelligence in Medicine",
        help="Describe the scientific topic for your document"
    )
    
    # Botón centrado y prominente
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🚀 Generate Document", 
            type="primary", 
            use_container_width=True,
            help="Click to start generating your scientific document"
        )

    # Procesamiento
    if generate_button:
        if not topic:
            st.error("Please enter a research topic.")
            return
        
        st.session_state.topic = topic
        st.session_state.fecha_actual = "June 2025"
        
        try:
            with st.spinner("Generating your scientific document..."):
                # Barra de progreso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                flow = ScientificDocumentFlow()
                
                # Simular progreso
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 25:
                        status_text.text("🔍 Researching...")
                    elif i < 50:
                        status_text.text("✍️ Writing...")
                    elif i < 75:
                        status_text.text("🖼️ Finding images...")
                    else:
                        status_text.text("📋 Structuring...")
                
                result = flow.kickoff()
                
                # Generar PDF
                status_text.text("📄 Generating PDF...")
                pdf_path = generar_pdf_desde_markdown(str(result), topic)
                
                progress_bar.empty()
                status_text.empty()
                
                if pdf_path and os.path.exists(pdf_path):
                    st.success("✅ Document generated successfully!")
                    
                    # Mostrar preview del contenido
                    with st.expander("📖 Document Preview", expanded=True):
                        # Mostrar solo las primeras líneas
                        preview_lines = str(result).split('\n')[:20]
                        preview_text = '\n'.join(preview_lines)
                        st.markdown(preview_text)
                        if len(str(result).split('\n')) > 20:
                            st.caption("... (document continues)")
                    
                    # Botón de descarga prominente
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_file.read(),
                            file_name=f"{topic.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                else:
                    st.error("Error generating PDF")
                    
        except Exception as e:
            st.error(f"Error during generation: {e}")

if __name__ == "__main__":
    main()
