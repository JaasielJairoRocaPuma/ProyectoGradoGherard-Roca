from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Comprobante, Firmas,DescripcionCuentas
from plancuentas.models import CuentaAuxiliar
from .forms import CreateNewComprobante, EditComprobante, CreateNewDescripcionCuenta, InsertNewComprobante, InsertNewComprobante2
from django.http import JsonResponse
import google.generativeai as genai
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm


GEN_API_KEY="AIzaSyAnrMV2Z0Zn9FT0sZeOD5WrlqQsTYPBi2A"
genai.configure(api_key=GEN_API_KEY)

# Create your views here.
def lista_comprobantes(request):
    comprobantes = Comprobante.objects.all().order_by('tipo', 'numero')
    firmas = Firmas.objects.all().order_by('nombre')
    cuentas = CuentaAuxiliar.objects.all().order_by('cuentamayor','nombre')
    
    # Procesar POST del formulario de creación
    if request.method == 'GET':
        data = []
        for c in comprobantes:
            cuentas_data = []
            total_debe = 0
            total_haber = 0
            total_diferencia = 0

            for cu in c.descripcionCuentas.all():
                diferencia = ((cu.debe or 0) - (cu.haber or 0)) / (c.tipocambio or 1)
                cuentas_data.append({
                    'codigo': cu.cuenta.codigo,
                    'nombre': cu.cuenta.nombre,
                    'debe': cu.debe or 0,
                    'haber': cu.haber or 0,
                    'diferencia': round(diferencia, 2)
                })
                total_debe += cu.debe or 0
                total_haber += cu.haber or 0
                total_diferencia += diferencia

            data.append({
                'numero': c.numero,
                'beneficiario': c.beneficiario,
                'fecha': c.fecha,
                'tipocambio': c.tipocambio,
                'cuentas': cuentas_data,
                'total_debe': total_debe,
                'total_haber': total_haber,
                'total_diferencia': round(total_diferencia, 2)
            })
            c.total_debe = total_debe
            c.total_haber = total_haber
            c.total_diferencia = round(total_diferencia, 2)

        return render(request, 'comprobantes/lista_comprobantes.html', {
            'data': data,
            'comprobantes': comprobantes,
            'formCreate': CreateNewComprobante(),
            'formCuenta': CreateNewDescripcionCuenta(),
            'firmas': firmas,
            'cuentas': cuentas,
            'formEdit': EditComprobante(),
            'formInsert': InsertNewComprobante(),
            'formInsertD': InsertNewComprobante2()
        })
    else:
        # Procesar eliminación de comprobante
        if request.POST.get('type') == 'eliminar':
            comprobante_id = request.POST.get('id')
            comprobante = get_object_or_404(Comprobante, id=comprobante_id)
            tipo_display = comprobante.get_tipo_display()
            numero = comprobante.numero
            comprobante.eliminar()
            messages.success(request, f'Comprobante {tipo_display} Nro: {numero} eliminado correctamente.')
            return redirect('comprobantes:lista_comprobantes')
        
        numero = request.POST.get('numero', '')
        if numero == '':
            comprobante = Comprobante.objects.create(
                fecha=request.POST['fecha'],
                glosa=request.POST['glosa'],
                beneficiario=request.POST['beneficiario'],
                tipocambio=request.POST['tipo-cambio'],
                ufv = request.POST['inputUfv'],
                tipo = request.POST['tipo'],
                imagen = request.POST['imagen']
            )
            
            # Firmas y cuentas desde inputs hidden
            firmas_ids = request.POST.getlist('firmas[]')
            cuentas_ids = request.POST.getlist('cuentas[]')
            debe_vals = request.POST.getlist('debe[]')
            haber_vals = request.POST.getlist('haber[]')
            
            cuentas_obj = []
            for cid, db, hb in zip(cuentas_ids, debe_vals, haber_vals):
                desc_cuenta = DescripcionCuentas.objects.create(
                    cuenta=get_object_or_404(CuentaAuxiliar, id=cid),
                    debe=db or 0,
                    haber=hb or 0
                )
                cuentas_obj.append(desc_cuenta)
            
            # Agregar comprobante usando tu método para autocompletar número
            comprobante.agregar(cuentas=cuentas_obj, firmas=firmas_ids)
        else:
            #llamar a la función insertar
            # Firmas y cuentas desde inputs hidden
            firmas_ids = request.POST.getlist('firmasi[]')
            cuentas_ids = request.POST.getlist('cuentasi[]')
            debe_vals = request.POST.getlist('debei[]')
            haber_vals = request.POST.getlist('haberi[]')

            # Crear objetos DescripcionCuentas
            cuentas_obj = []
            for cid, db, hb in zip(cuentas_ids, debe_vals, haber_vals):
                desc_cuenta = DescripcionCuentas.objects.create(
                    cuenta=get_object_or_404(CuentaAuxiliar, id=cid),
                    debe=db or 0,
                    haber=hb or 0
                )
                cuentas_obj.append(desc_cuenta)
            Comprobante.insertar(
                posicion=request.POST['numero'],
                glosa=request.POST['glosa'], 
                fecha=request.POST['fecha-i'],
                beneficiario=request.POST['beneficiario'],
                tipocambio=request.POST['tipo-cambio-i'],
                ufv = request.POST['inputUfv-i'],
                tipo = request.POST['tipo'],
                cuentas=cuentas_obj,
                firmas=firmas_ids
            )
        
        return redirect(request.path)  # Ajusta tu URL


def detalle_comprobante(request, id):
    """
    Vista detallada del comprobante que renderiza vista_comprobante.html
    con todos los datos necesarios: comprobante, descripcioncuentas y firmas.
    """
    comprobante = get_object_or_404(Comprobante, id=id)
    
    # Obtener todas las descripciones de cuentas (DescripcionCuentas)
    descripcion_cuentas = comprobante.descripcionCuentas.all()
    
    # Preparar datos de cuentas con diferencias
    cuentas_data = []
    total_debe = 0
    total_haber = 0
    total_diferencia = 0
    
    for desc_cuenta in descripcion_cuentas:
        debe = desc_cuenta.debe or 0
        haber = desc_cuenta.haber or 0
        diferencia = (debe - haber) / (comprobante.tipocambio or 1)
        
        cuentas_data.append({
            'codigo': desc_cuenta.cuenta.codigo,
            'nombre': desc_cuenta.cuenta.nombre,
            'debe': debe,
            'haber': haber,
            'diferencia': round(diferencia, 2)
        })
        
        total_debe += debe
        total_haber += haber
        total_diferencia += diferencia
    
    # Obtener firmas responsables
    firmas_responsables = comprobante.responsables.all()
    
    return render(request, 'comprobantes/vista_comprobante.html', {
        'comprobante': comprobante,
        'descripcion_cuentas': descripcion_cuentas,
        'cuentas_data': cuentas_data,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'total_diferencia': round(total_diferencia, 2),
        'firmas_responsables': firmas_responsables
    })

def vista_comprobante(request, id):
    """
    Vista detallada del comprobante con todos los datos,
    glosa, beneficiario, firmas y botón para imprimir PDF.
    """
    comprobante = get_object_or_404(Comprobante, id=id)
    
    # Obtener todas las descripciones de cuentas (DescripcionCuentas)
    descripcion_cuentas = comprobante.descripcionCuentas.all()
    
    # Preparar datos de cuentas con diferencias
    cuentas_data = []
    total_debe = 0
    total_haber = 0
    total_diferencia = 0
    
    for desc_cuenta in descripcion_cuentas:
        debe = desc_cuenta.debe or 0
        haber = desc_cuenta.haber or 0
        diferencia = (debe - haber) / (comprobante.tipocambio or 1)
        
        cuentas_data.append({
            'codigo': desc_cuenta.cuenta.codigo,
            'nombre': desc_cuenta.cuenta.nombre,
            'debe': debe,
            'haber': haber,
            'diferencia': round(diferencia, 2)
        })
        
        total_debe += debe
        total_haber += haber
        total_diferencia += diferencia
    
    # Obtener firmas responsables
    firmas_responsables = comprobante.responsables.all()
    
    return render(request, 'comprobantes/vista_comprobante.html', {
        'comprobante': comprobante,
        'descripcion_cuentas': descripcion_cuentas,
        'cuentas_data': cuentas_data,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'total_diferencia': round(total_diferencia, 2),
        'firmas_responsables': firmas_responsables
    })



def obtener_ufv_gpt(request):
    fecha = request.GET.get('fecha')  # formato YYYY-MM-DD
    if not fecha:
        return JsonResponse({"error": "Fecha no proporcionada"}, status=400)

    prompt = f"¿Cuál es el valor de la UFV en Bolivia para la fecha {fecha}? Devuélvelo solo como número, sin texto adicional."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        ufv_texto = response.text.strip()
        
        # Convertir a float (reemplaza coma por punto si la hay)
        ufv = float(ufv_texto.replace(',', '.'))
        return JsonResponse({"ufv": ufv})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def reporte_comprobantes_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="comprobantes.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    title = Paragraph("LIBRO DIARIO", styles['Title'])

    elements = [title, Spacer(1, 12)]

    comprobantes = Comprobante.objects.all().order_by("tipo", "numero")

    for comp in comprobantes:
        # --------------------------
        # 1) ENCABEZADO NEGRO (Tipo/Numero  |  Fecha + TipoCambio)
        # --------------------------
        encabezado = Table(
            [[
                f"{comp.get_tipo_display()} Nro: {comp.numero}",
                f"Fecha: {comp.fecha.strftime('%d/%m/%Y')}\nT. Cambio: {float(comp.tipocambio):,.4f}"
            ]],
            colWidths=[10*cm, 6.5*cm]
        )
        encabezado.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.black),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))

        # --------------------------
        # 2) FILA BENEFICIARIO + GLOSA (misma tarjeta)
        # --------------------------
        beneficiario_cell = Paragraph(f"<b>Beneficiario:</b> {comp.beneficiario}", normal)
        glosa_cell = Paragraph(f"<b>Glosa:</b> {comp.glosa}", normal)

        beneficiario_glosa = Table(
            [[beneficiario_cell, glosa_cell]],
            colWidths=[10*cm, 6.5*cm]
        )
        beneficiario_glosa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,-1), "Helvetica"),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))

        # --------------------------
        # 3) TABLA DE CUENTAS
        # --------------------------
        cuentas_data = [["Cuenta", "Debe", "Haber", "Diferencia"]]
        total_debe = 0
        total_haber = 0

        for dc in comp.descripcionCuentas.all():
            debe = dc.debe or 0
            haber = dc.haber or 0
            diff = float(debe) - float(haber)

            cuentas_data.append([
                Paragraph(f"{dc.cuenta.codigo}  {dc.cuenta.nombre}", normal),
                f"{debe:,.2f}",
                f"{haber:,.2f}",
                f"{diff:,.2f}"
            ])

            total_debe += float(debe)
            total_haber += float(haber)

        cuentas_data.append([
            Paragraph("<b>TOTAL</b>", normal),
            f"{total_debe:,.2f}",
            f"{total_haber:,.2f}",
            f"{(total_debe - total_haber):,.2f}"
        ])

        tabla_cuentas = Table(
            cuentas_data,
            colWidths=[9*cm, 2.5*cm, 2.5*cm, 2.5*cm]
        )
        tabla_cuentas.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))

        # --------------------------
        # 4) UNIR TODO EN UNA TARJETA (una sola tabla con 3 filas: encabezado, beneficiario/glosa, cuentas)
        # --------------------------
        tarjeta = Table(
            [
                [encabezado],
                [beneficiario_glosa],
                [tabla_cuentas]
            ],
            colWidths=[17*cm]
        )
        tarjeta.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.2, colors.white),  # limpia separación interna
        ]))

        elements.append(tarjeta)
        elements.append(Spacer(1, 12))  # separación entre comprobantes

    doc.build(elements)
    return response

def imprimir_comprobante_pdf(request, id):
    """
    Genera un PDF individual para un comprobante específico con formato tipo recibo/factura.
    """
    comprobante = get_object_or_404(Comprobante, id=id)
    
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="comprobante_{comprobante.tipo}_{comprobante.numero}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, 
                           leftMargin=2*cm, rightMargin=2*cm, 
                           topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles['Heading2']
    
    # Estilos personalizados
    title_style = styles['Title']
    title_style.fontSize = 24
    title_style.textColor = colors.HexColor('#1a1a1a')
    title_style.alignment = 1  # Centrado
    
    elements = []

    # ========== ENCABEZADO TIPO FACTURA ==========
    # Título principal centrado
    titulo = Paragraph(
        f"<b>{comprobante.get_tipo_display().upper()}</b>", 
        title_style
    )
    elements.append(titulo)
    
    # Número de comprobante
    numero_para = Paragraph(f'<b>Número: {comprobante.numero}</b>', normal)
    numero_para.style.fontSize = 14
    numero_para.style.alignment = 1
    elements.append(numero_para)
    elements.append(Spacer(1, 0.5*cm))
    
    # Línea separadora
    elements.append(Spacer(1, 0.3*cm))
    
    # ========== INFORMACIÓN DEL COMPROBANTE ==========
    info_data = [
        [
            Paragraph('<b>Fecha:</b>', normal),
            Paragraph(comprobante.fecha.strftime('%d/%m/%Y'), normal),
            Paragraph('<b>Tipo de Cambio:</b>', normal),
            Paragraph(f"{float(comprobante.tipocambio):,.4f}", normal)
        ],
        [
            Paragraph('<b>UFV:</b>', normal),
            Paragraph(f"{float(comprobante.ufv):,.6f}", normal),
            Paragraph('<b>Beneficiario:</b>', normal),
            Paragraph(comprobante.beneficiario, normal)
        ]
    ]
    
    tabla_info = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    tabla_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(tabla_info)
    elements.append(Spacer(1, 0.5*cm))
    
    # Glosa
    glosa_box = Table(
        [[Paragraph(f'<b>Glosa:</b> {comprobante.glosa}', normal)]],
        colWidths=[17*cm]
    )
    glosa_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(glosa_box)
    elements.append(Spacer(1, 0.8*cm))
    
    # ========== TABLA DE CUENTAS CONTABLES ==========
    elements.append(Paragraph('<b>DETALLE DE CUENTAS CONTABLES</b>', heading))
    elements.append(Spacer(1, 0.3*cm))
    
    cuentas_data = [
        ["Código", "Nombre de la Cuenta", "Debe (Bs.)", "Haber (Bs.)", "Diferencia (USD)"]
    ]
    total_debe = 0
    total_haber = 0

    for dc in comprobante.descripcionCuentas.all():
        debe = float(dc.debe or 0)
        haber = float(dc.haber or 0)
        diff = (debe - haber) / float(comprobante.tipocambio)

        cuentas_data.append([
            Paragraph(dc.cuenta.codigo, normal),
            Paragraph(dc.cuenta.nombre, normal),
            f"{debe:,.2f}",
            f"{haber:,.2f}",
            f"{diff:,.2f}"
        ])

        total_debe += debe
        total_haber += haber

    # Fila de totales
    total_diff = (total_debe - total_haber) / float(comprobante.tipocambio)
    cuentas_data.append([
        Paragraph("<b>TOTALES</b>", normal),
        '',
        Paragraph(f"<b>{total_debe:,.2f}</b>", normal),
        Paragraph(f"<b>{total_haber:,.2f}</b>", normal),
        Paragraph(f"<b>{total_diff:,.2f}</b>", normal)
    ])

    tabla_cuentas = Table(
        cuentas_data,
        colWidths=[2.5*cm, 7*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    )
    tabla_cuentas.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (2,0), (-1,0), 'CENTER'),
        
        # Filas de datos
        ('FONTNAME', (0,1), (-2,-2), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ALIGN', (2,1), (-1,-2), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Fila de totales
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 10),
        ('ALIGN', (2,-1), (-1,-1), 'RIGHT'),
        
        # Bordes
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor('#667eea')),
        ('LINEABOVE', (0,-1), (-1,-1), 2, colors.HexColor('#495057')),
        
        # Padding
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(tabla_cuentas)
    elements.append(Spacer(1, 1*cm))
    
    # ========== FIRMAS RESPONSABLES ==========
    if comprobante.responsables.exists():
        elements.append(Paragraph('<b>FIRMAS RESPONSABLES</b>', heading))
        elements.append(Spacer(1, 0.3*cm))
        
        firmas_data = [["Nombre Completo", "Cargo", "C.I."]]
        for firma in comprobante.responsables.all():
            firmas_data.append([
                firma.nombre,
                firma.cargo,
                f"{firma.ci} {firma.get_extencion_display()}"
            ])

        tabla_firmas = Table(
            firmas_data,
            colWidths=[7*cm, 6*cm, 4*cm]
        )
        tabla_firmas.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            
            # Filas de datos
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Bordes
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor('#6c757d')),
            
            # Padding
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(tabla_firmas)
        elements.append(Spacer(1, 1.5*cm))
        
        # Área de firmas (espacios para firmas manuscritas)
        espacios_firmas = []
        for firma in comprobante.responsables.all():
            espacios_firmas.append([
                Paragraph(f"_____________________<br/>{firma.nombre}<br/>{firma.cargo}", normal)
            ])
        
        if espacios_firmas:
            tabla_espacios = Table(espacios_firmas, colWidths=[17*cm / len(espacios_firmas)])
            tabla_espacios.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 15),
            ]))
            elements.append(tabla_espacios)
    
    # Pie de página
    elements.append(Spacer(1, 1*cm))
    from datetime import datetime
    fecha_impresion = Paragraph(
        f'<i>Documento generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}</i>',
        normal
    )
    elements.append(fecha_impresion)
    
    doc.build(elements)
    return response