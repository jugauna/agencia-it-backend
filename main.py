from fastapi import FastAPI
from pydantic import BaseModel
from fpdf import FPDF
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path
import uuid

app = FastAPI()

# Configuración de CORS para que tu web en Hostinger pueda hablar con este script
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class ItemServicio(BaseModel):
    servicio: str
    horas: float
    precio: float

class PropuestaData(BaseModel):
    empresa: str
    proyecto: str
    items: list[ItemServicio]

# Función para limpiar nombres de archivos (evita errores en Windows)
def limpiar_nombre(texto: str):
    return "".join([c for c in texto if c.isalnum() or c in (' ', '_')]).strip()

@app.post("/crear-propuesta")
async def crear_propuesta(data: PropuestaData):
    # 1. Configuración del PDF
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

    # --- LÓGICA DE GUARDADO EN CARPETA LOCAL C:\ ---
    
    # Definimos la ruta base en Windows
    base_path = Path(r"C:\Presupuestos_testing")
    
    # Limpiamos nombres para evitar caracteres prohibidos como / \ : * ? " < > |
    empresa_clean = limpiar_nombre(data.empresa)
    proyecto_clean = limpiar_nombre(data.proyecto)
    
    # Creamos la subcarpeta de la empresa (C:\Presupuestos_testing\Nombre_Empresa)
    folder_destino = base_path / empresa_clean
    folder_destino.mkdir(parents=True, exist_ok=True)
    
    # Nombre final del archivo (Proyecto.pdf)
    filename = f"{proyecto_clean}.pdf"
    filepath = folder_destino / filename
    
    # Guardar el PDF físicamente en el disco C:
    pdf.output(str(filepath))
    
    # 5. Enviar el archivo para que el navegador lo descargue también
    return FileResponse(
        path=str(filepath), 
        filename=filename, 
        media_type='application/pdf'
    )

if __name__ == "__main__":
    import uvicorn
    # Para correrlo localmente: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)