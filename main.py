from fastapi import FastAPI
from pydantic import BaseModel
from fpdf import FPDF
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI()

# Configuración de CORS para permitir peticiones desde Hostinger
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    # --- DISEÑO DEL PDF ---
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 255, 204) 
    pdf.cell(190, 20, txt="PROPUESTA TÉCNICA Y ECONÓMICA", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(25)
    pdf.cell(100, 10, txt=f"Cliente: {data.empresa}")
    pdf.cell(100, 10, txt=f"Proyecto: {data.proyecto}", ln=True)
    
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
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 12, txt="INVERSIÓN TOTAL ESTIMADA ", border=0, align='R')
    pdf.set_text_color(0, 150, 120)
    pdf.cell(50, 12, txt=f"${total:,.2f}", border=1, ln=True, align='C')

    # --- GENERACIÓN DEL ARCHIVO ---
    file_id = str(uuid.uuid4())[:8]
    filename = f"propuesta_{data.empresa.replace(' ', '_')}_{file_id}.pdf"
    filepath = os.path.join("/tmp", filename) if os.path.exists("/tmp") else filename
    
    pdf.output(filepath)
    
    # Retornamos el archivo para descarga automática
    return FileResponse(
        path=filepath, 
        filename=filename, 
        media_type='application/pdf'
    )