from fastapi import FastAPI
from pydantic import BaseModel
from fpdf import FPDF
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

# CONFIGURACIÓN DE SEGURIDAD (CORS)
# Esto permite que tu WordPress en Hostinger se conecte a Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, podés poner tu dominio específico
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructura de los datos que vienen desde Divi
class ItemServicio(BaseModel):
    servicio: str
    horas: float
    precio: float

class PropuestaData(BaseModel):
    empresa: str
    proyecto: str
    items: list[ItemServicio]

@app.post("/crear-propuesta")
async def crear_propuesta(data: PropuestaData):
    pdf = FPDF()
    pdf.add_page()
    
    # Diseño de Cabecera (Estilo IT Agency)
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 255, 204) # Color Cian IT
    pdf.cell(190, 20, txt="PROPUESTA TÉCNICA Y ECONÓMICA", ln=True, align='C')
    
    # Información del Cliente
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(25)
    pdf.cell(100, 10, txt=f"Cliente: {data.empresa}")
    pdf.cell(100, 10, txt=f"Proyecto: {data.proyecto}", ln=True)
    
    # Tabla de Ítems
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(110, 10, txt=" Servicio / Concepto", border=1, fill=True)
    pdf.cell(30, 10, txt=" Cant.", border=1, fill=True, align='C')
    pdf.cell(50, 10, txt=" Subtotal", border=1, fill=True, align='C', ln=True)
    
    total = 0
    pdf.set_font("Arial", '', 10)
    for item in data.items:
        subtotal = item.horas * item.precio
        pdf.cell(110, 10, txt=f" {item.servicio}", border=1)
        pdf.cell(30, 10, txt=f"{item.horas}", border=1, align='C')
        pdf.cell(50, 10, txt=f"${subtotal:,.2f}", border=1, ln=True, align='C')
        total += subtotal
        
    # Total Final
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 12, txt="INVERSIÓN TOTAL ESTIMADA ", border=0, align='R')
    pdf.set_text_color(0, 150, 120)
    pdf.cell(50, 12, txt=f"${total:,.2f}", border=1, ln=True, align='C')
    
    # Pie de página legal
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(190, 5, txt="Esta propuesta tiene carácter confidencial y una validez de 15 días corridos. Los servicios de IT están sujetos a términos de mantenimiento anual.")

    # Nombre único para el archivo
    file_id = str(uuid.uuid4())[:8]
    filename = f"propuesta_{data.empresa.replace(' ', '_')}_{file_id}.pdf"
    
    # Guardar localmente en el contenedor (Render lo borrará al reiniciar, ideal por privacidad)
    pdf.output(filename)
    
    return {
        "mensaje": f"Propuesta para {data.empresa} generada con éxito",
        "total": total,
        "archivo_generado": filename
    }