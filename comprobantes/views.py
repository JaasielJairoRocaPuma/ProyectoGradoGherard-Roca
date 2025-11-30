from django.shortcuts import render, get_object_or_404, redirect
from .models import Comprobante, Firmas,DescripcionCuentas
from plancuentas.models import CuentaAuxiliar
from .forms import CreateNewComprobante, EditComprobante, CreateNewDescripcionCuenta
from django.http import JsonResponse
import google.generativeai as genai


GEN_API_KEY="AIzaSyC-YtnUd4zZcSOX_jQLnMdrmWr-KU17VjQ"
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
            'formEdit': EditComprobante()
        })
    else:
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
        
        return redirect(request.path)  # Ajusta tu URL


def detalle_comprobante(request, id):
    comprobante = get_object_or_404(Comprobante, id=id)
    for cu in comprobante.descripcionCuentas.all():  # supondremos que es un related_name
        cu.diferencia = (cu.debe or 0 - cu.haber or 0) / (comprobante.tipocambio or 1)

    return render(request, 'comprobantes/comprobante.html', {'comprobante': comprobante})

def insertar_comprobante(request):
    Comprobante.insertar(
        numero= request.POST['numeroC'],
        posicion=request.POST['posicion'],
        glosa=request.POST['glosa'],
        fecha=request.POST['fecha'],
        beneficiario=request.POST['beneficiario'],
        tipocambio=request.POST['tipo-cambio'],
        ufv = request.POST['inputUfv'],
        tipo = request.POST['tipo'],
        cuentas=[],
        firmas=[]
    )

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