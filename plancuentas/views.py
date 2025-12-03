# Archivo: plancuentas/views.py
# Descripción: Define las vistas para el módulo de Plan de Cuentas.
# Incluye vistas para listar, crear, editar y gestionar cuentas contables.

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Grupo, SubGrupo, CuentaMatriz, CuentaMayor, CuentaAuxiliar
from .forms import CreateNewCuentaAuxiliar, EditCuentaAuxiliar
from openpyxl import Workbook #reportes en excel
from reportlab.pdfgen import canvas #reportes en pdf
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def ListaPlanCuentasView(request):
    grupos = Grupo.objects.all()
    subgrupos = SubGrupo.objects.all()
    cuentas_matriz = CuentaMatriz.objects.all()
    cuentas_mayor = CuentaMayor.objects.all()
    cuentas_auxiliar = CuentaAuxiliar.objects.all()

    if request.method == "GET":
        return render(request, 'plancuentas/lista_cuentas.html', {
            'grupos': grupos,
            'subgrupos': subgrupos,
            'cuentas_matriz': cuentas_matriz,
            'cuentas_mayor': cuentas_mayor,
            'cuentas_auxiliar': cuentas_auxiliar,
            'form': CreateNewCuentaAuxiliar(),
            'formE': EditCuentaAuxiliar()
            })
    else:
        if request.POST['type'] == 'crear':
            CuentaAuxiliar.objects.create(
                cod=request.POST['cod'],
                nombre=request.POST['nombre'],
                cuentamayor=get_object_or_404(CuentaMayor, id=request.POST['cuentamayor']),
                tipo=request.POST['tipo'],
            )
        elif request.POST['type']=='borrar':
            ca=CuentaAuxiliar.objects.filter(id=request.POST['id']).first()
            ca.delete()
        else:
            ca=CuentaAuxiliar.objects.filter(id=request.POST['id']).first()
            ca.nombre=request.POST['nombre']
            ca.save()
        return redirect(request.path)

def reporte_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Plan de Cuentas"

    # Encabezados
    ws.append(["Codigo", "Descripcion", "Tipo", "Nivel"])

    # Datos del modelo

    for g in Grupo.objects.all():
        ws.append([g.codigo, g.nombre, g.tipo, g.nivel])
        for sg in SubGrupo.objects.filter(grupo=g):
            ws.append([sg.codigo, sg.nombre, sg.tipo, sg.nivel])
            for cm in CuentaMatriz.objects.filter(subgrupo=sg):
                ws.append([cm.codigo, cm.nombre, cm.tipo, cm.nivel])
                for cma in CuentaMayor.objects.filter(cuentamatriz=cm):
                    ws.append([cma.codigo, cma.nombre, cma.tipo, cma.nivel])
                    for ca in CuentaAuxiliar.objects.filter(cuentamayor=cma):
                        ws.append([ca.codigo, ca.nombre, ca.tipo, ca.nivel])

    # Respuesta HTTP para descargar
    response = HttpResponse(
        content_type="application/ms-excel",
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_plan_de_cuentas.xlsx"'
    wb.save(response)
    return response
    
def reporte_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="reporte_plan_cuentas.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("PLAN DE CUENTAS", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Cabecera
    data = [["Código", "Descripción", "Tipo", "Nivel"]]

    # Para poder aplicar negrillas luego, guardamos índices
    rows_with_bold = []

    def add_row(model, codigo_prefix=""):
        """Agrega la fila a data y devuelve si debe ir en negrilla."""
        codigo = codigo_prefix + model.codigo
        data.append([codigo, model.nombre, model.tipo, model.nivel])

        # Devuelve True si es nivel 1 a 4
        return model.nivel and int(model.nivel) in (1, 2, 3, 4)

    # Llenado de datos
    for g in Grupo.objects.all():
        if add_row(g):
            rows_with_bold.append(len(data)-1)

        for sg in SubGrupo.objects.filter(grupo=g):
            if add_row(sg, ""):
                rows_with_bold.append(len(data)-1)

            for cm in CuentaMatriz.objects.filter(subgrupo=sg):
                if add_row(cm, ""):
                    rows_with_bold.append(len(data)-1)

                for cma in CuentaMayor.objects.filter(cuentamatriz=cm):
                    if add_row(cma, ""):
                        rows_with_bold.append(len(data)-1)

                    for ca in CuentaAuxiliar.objects.filter(cuentamayor=cma):
                        if add_row(ca, ""):
                            rows_with_bold.append(len(data)-1)

    # Crear tabla
    table = Table(data, colWidths=[80, 260, 60, 30])

    # Estilos generales
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
    ])

    # 🔥 Agregar negrillas dinámicas a las filas nivel 1 a 4
    for row_index in rows_with_bold:
        style.add('FONTNAME', (0, row_index), (-1, row_index), 'Helvetica-Bold')

    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    return response