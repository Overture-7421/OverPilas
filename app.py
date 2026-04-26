from flask import Flask, request, render_template, redirect
import json, os, sys
from datetime import datetime, timedelta

if getattr(sys, 'frozen', False):
    _base = sys._MEIPASS
    app = Flask(__name__,
                template_folder=os.path.join(_base, 'templates'),
                static_folder=os.path.join(_base, 'static'))
else:
    app = Flask(__name__)
data_file = 'pilas.json'

categorias_inventario = ["Mecánica", "Eléctrica", "Scouting", "Negocios"]

# Lista fija de nombres
nombres_fijos = ["Western Bacon", "Bolillo", "Marcela", "Billie", "Simi","Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird", 
                "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
                "Ada", "Jorge",
                "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def guardar_datos():
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'inventario_items': inventario_items
    }
    with open(data_file, 'w') as f:
        json.dump(data_to_save, f)

def es_pila_lista_para_conectar(nombre):
    """Verifica si una pila está lista para conectar"""
    # Si no tiene datos, está lista para conectar
    pila = next((p for p in pilas if p['nombre'] == nombre), None)
    if not pila:
        return True
    
    # Si está en cooldown, verificar si han pasado 30 minutos
    if nombre in pilas_en_cooldown:
        timestamp_cooldown = datetime.strptime(pilas_en_cooldown[nombre], "%Y-%m-%d %H:%M")
        tiempo_transcurrido = datetime.now() - timestamp_cooldown
        return tiempo_transcurrido.total_seconds() >= 1800  # 30 minutos = 1800 segundos
    
    return False

def obtener_pilas_listas_para_conectar():
    """Obtiene lista de pilas listas para conectar ordenadas por tiempo sin conectar"""
    global pilas_en_cooldown, pilas_inhabilitadas
    pilas_listas = []
    cooldowns_a_limpiar = []
    
    for nombre in nombres_fijos:
        if nombre in pilas_en_uso:
            continue  # Saltar pilas que estén en uso
            
        if es_pila_lista_para_conectar(nombre):
            # Determinar tiempo sin conectar
            tiempo_sin_conectar = None
            
            # Si está en cooldown y ya pasó el tiempo
            if nombre in pilas_en_cooldown:
                timestamp_cooldown = datetime.strptime(pilas_en_cooldown[nombre], "%Y-%m-%d %H:%M")
                tiempo_transcurrido = datetime.now() - timestamp_cooldown
                
                # Si ya pasaron 30 minutos, marcar para limpiar del cooldown
                if tiempo_transcurrido.total_seconds() >= 1800:
                    cooldowns_a_limpiar.append(nombre)
                    tiempo_sin_conectar = timestamp_cooldown
                else:
                    continue  # Todavía está en cooldown, no agregarlo a la lista
            else:
                # Si no tiene datos, usar tiempo muy antiguo para que aparezca primero
                tiempo_sin_conectar = datetime(2000, 1, 1)
            
            pilas_listas.append({
                'nombre': nombre,
                'tiempo_sin_conectar': tiempo_sin_conectar,
                'disabled': (nombre in pilas_inhabilitadas)
            })
    
    # Limpiar cooldowns que ya completaron los 30 minutos
    for nombre in cooldowns_a_limpiar:
        del pilas_en_cooldown[nombre]
    
    # Si se limpiaron cooldowns, guardar los cambios
    if cooldowns_a_limpiar:
        guardar_datos()
    
    # Ordenar: primero por disabled (False primero), luego por tiempo sin conectar (más antiguos primero)
    pilas_listas.sort(key=lambda x: (x.get('disabled', False), x['tiempo_sin_conectar']))
    
    return pilas_listas

# Cargar datos existentes de forma segura
pilas = []
ultima_actualizacion = None  # Guardará la fecha y hora
# Ahora soportamos hasta 2 pilas en uso
pilas_en_uso = []  # Lista de nombres de pilas en uso
# Guardará {nombre: timestamp} de pilas en cooldown
pilas_en_cooldown = {}
# Pilas inhabilitadas (no aparecerán como "listas" y se mostrarán gris)
pilas_inhabilitadas = set()
# Inventario persistente
inventario_items = []
# Nota: mantenemos compatibilidad con el formato antiguo que usaba 'pila_en_uso'
if os.path.exists(data_file):
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                # Formato anterior - solo lista de pilas
                pilas = data
            else:
                # Formato nuevo - objeto con pilas, pilas_en_uso/pila_en_uso y cooldowns
                pilas = data.get('pilas', [])
                # Compatibilidad: si existe 'pila_en_uso' (string), convertir a lista
                if 'pilas_en_uso' in data:
                    pilas_en_uso = data.get('pilas_en_uso') or []
                else:
                    single = data.get('pila_en_uso', None)
                    pilas_en_uso = [single] if single else []
                pilas_en_cooldown = data.get('pilas_en_cooldown', {})
                pilas_inhabilitadas = set(data.get('pilas_inhabilitadas', []) or [])
                inventario_items = data.get('inventario_items', []) or []
    except json.JSONDecodeError:
        pilas = []

@app.route('/')
def index():
    active_tab = request.args.get('tab', 'pilas')
    active_inv_section = request.args.get('inv_section', '')

    # Crear lista completa para mostrar
    listado = []
    for nombre in nombres_fijos:
        pila = next((p for p in pilas if p['nombre'] == nombre), None)
        if pila:
            listado.append(pila)
        else:
            listado.append({"nombre": nombre, "carga": "Sin datos", "ohms": "Sin datos"})

    # Ordenar por Ohms (menor a mayor) y luego por Carga (mayor a menor)
    def key_ordenamiento(p):
        try:
            carga = float(p['carga'])
        except:
            # "Sin datos" se coloca al final con carga muy baja
            carga = -1
        
        try:
            ohms = float(p['ohms'])
        except:
            # Si no hay ohms válidos, usar valor alto para que vaya al final
            ohms = 999999
        
        # Retornar tupla: (ohms para orden ascendente, carga negativa para orden descendente)
        return (ohms, -carga)
    
    listado_ordenado = sorted(listado, key=key_ordenamiento)

    # Calcular próximo chequeo si hay última actualización
    proximo_chequeo = None
    if ultima_actualizacion:
        try:
            # Convertir la fecha de string a datetime y sumar 30 minutos
            fecha_actualizacion = datetime.strptime(ultima_actualizacion, "%Y-%m-%d %H:%M")
            proximo = fecha_actualizacion + timedelta(minutes=30)
            proximo_chequeo = proximo.strftime("%H:%M")
        except:
            proximo_chequeo = None

    # Obtener pilas listas para conectar
    pilas_listas = obtener_pilas_listas_para_conectar()

    # Determinar la mejor pila disponible (primera con carga válida, no en uso y no en cooldown)
    mejor_pila = None
    for p in listado_ordenado:
        try:
            if p.get('carga') != 'Sin datos' and p.get('nombre') not in pilas_en_uso and p.get('nombre') not in pilas_en_cooldown:
                mejor_pila = p.get('nombre')
                break
        except Exception:
            continue

    inventario_por_categoria = {}
    for categoria in categorias_inventario:
        # Mantener orden de inserción para que los objetos nuevos queden al final de la lista.
        inventario_por_categoria[categoria] = [
            item for item in inventario_items if item.get('categoria') == categoria
        ]

    def estado_checkout(item):
        estado = item.get('checkout_state')
        if estado in ('pending', 'retry', 'checked'):
            return estado
        return 'checked' if item.get('checked_out', False) else 'pending'

    checkout_pendientes_lista = [item for item in inventario_items if estado_checkout(item) == 'pending']
    checkout_reintentos_lista = [item for item in inventario_items if estado_checkout(item) == 'retry']
    checkout_actual = checkout_pendientes_lista[0] if checkout_pendientes_lista else (
        checkout_reintentos_lista[0] if checkout_reintentos_lista else None
    )

    return render_template(
        'index.html',
        pilas=listado_ordenado,
        ultima_actualizacion=ultima_actualizacion,
        proximo_chequeo=proximo_chequeo,
        pilas_en_uso=pilas_en_uso,
        pilas_en_cooldown=pilas_en_cooldown,
        pilas_listas=pilas_listas,
        mejor_pila=mejor_pila,
        pilas_inhabilitadas=list(pilas_inhabilitadas),
        nombres_fijos=nombres_fijos,
        active_tab=active_tab,
        active_inv_section=active_inv_section,
        categorias_inventario=categorias_inventario,
        inventario_por_categoria=inventario_por_categoria,
        inventario_total=len(inventario_items),
        checkout_pendientes=len(checkout_pendientes_lista) + len(checkout_reintentos_lista),
        checkout_actual=checkout_actual
    )

@app.route('/agregar', methods=['POST'])
def agregar():
    global ultima_actualizacion

    nombre = request.form['nombre']
    carga = request.form['carga']
    ohms = request.form['ohms']

    # Reemplazar si ya existe
    encontrado = False
    for i, pila in enumerate(pilas):
        if pila['nombre'] == nombre:
            pilas[i] = {"nombre": nombre, "carga": carga, "ohms": ohms}
            encontrado = True
            break
    if not encontrado:
        pilas.append({"nombre": nombre, "carga": carga, "ohms": ohms})

    # Guardar en JSON con nuevo formato
    guardar_datos()

    # Guardar fecha y hora de actualización
    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")

    return redirect('/')

@app.route('/pila_en_uso', methods=['POST'])
def marcar_pila_en_uso():
    global pilas_en_uso

    nombre = request.form['nombre']
    # Si no está en la lista de pilas en uso, agregarla (sin límite)
    if nombre not in pilas_en_uso:
        pilas_en_uso.append(nombre)

    # Borrar los datos de la pila seleccionada de la lista de pilas registradas
    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]

    # Guardar en JSON con nuevo formato
    guardar_datos()

    return redirect('/')


@app.route('/toggle_inhabilitar', methods=['POST'])
def toggle_inhabilitar():
    global pilas_inhabilitadas
    nombre = request.form.get('nombre')
    if not nombre:
        return redirect('/')

    if nombre in pilas_inhabilitadas:
        pilas_inhabilitadas.remove(nombre)
    else:
        pilas_inhabilitadas.add(nombre)

    # Guardar cambios
    guardar_datos()

    return redirect('/')

@app.route('/recibir_pila', methods=['POST'])
def recibir_pila():
    global pilas_en_cooldown
    
    nombre = request.form['nombre']
    
    # Remover de pila_en_uso si era la que estaba en uso
    global pilas_en_uso
    try:
        if nombre in pilas_en_uso:
            pilas_en_uso = [p for p in pilas_en_uso if p != nombre]
    except Exception:
        pilas_en_uso = []
    
    # Borrar los datos de la pila si existen
    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]
    
    # Marcar como en cooldown con timestamp actual
    pilas_en_cooldown[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Guardar en JSON con nuevo formato
    guardar_datos()
    
    return redirect('/')

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global pilas, pilas_en_uso, pilas_en_cooldown, ultima_actualizacion, inventario_items

    # Reiniciar todas las variables globales
    pilas = []
    pilas_en_uso = []
    pilas_en_cooldown = {}
    inventario_items = []
    ultima_actualizacion = None

    # Guardar el estado limpio en JSON
    guardar_datos()
    
    return redirect('/')

@app.route('/inventario/checkin', methods=['POST'])
def inventario_checkin():
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '').strip()
    cantidad_raw = request.form.get('cantidad', '1').strip() or '1'

    try:
        cantidad = int(cantidad_raw)
    except ValueError:
        cantidad = 1

    if cantidad < 1:
        cantidad = 1

    if not nombre or categoria not in categorias_inventario:
        return redirect('/?tab=inventario&inv_section=checkin')

    existente = next(
        (
            item for item in inventario_items
            if item.get('categoria') == categoria and item.get('nombre', '').lower() == nombre.lower()
        ),
        None
    )

    if existente:
        existente['cantidad'] = int(existente.get('cantidad', 0)) + cantidad
        existente['checked_out'] = False
        existente['checkout_state'] = 'pending'
        existente['last_checked_out'] = None
    else:
        inventario_items.append({
            'id': f"inv-{int(datetime.now().timestamp() * 1000)}-{len(inventario_items) + 1}",
            'nombre': nombre,
            'cantidad': cantidad,
            'categoria': categoria,
            'checked_out': False,
            'checkout_state': 'pending',
            'last_checked_out': None,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    guardar_datos()
    return redirect('/?tab=inventario&inv_section=checkin')

@app.route('/inventario/iniciar_checkout', methods=['POST'])
def inventario_iniciar_checkout():
    for item in inventario_items:
        item['checked_out'] = False
        item['checkout_state'] = 'pending'
        item['last_checked_out'] = None

    guardar_datos()
    return redirect('/?tab=inventario')

@app.route('/inventario/check_item', methods=['POST'])
def inventario_check_item():
    item_id = request.form.get('id', '').strip()
    if not item_id:
        return redirect('/?tab=inventario&inv_section=checkout')

    item = next((it for it in inventario_items if it.get('id') == item_id), None)
    if item:
        item['checked_out'] = True
        item['checkout_state'] = 'checked'
        item['last_checked_out'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        guardar_datos()

    return redirect('/?tab=inventario&inv_section=checkout')

@app.route('/inventario/check_item_missing', methods=['POST'])
def inventario_check_item_missing():
    item_id = request.form.get('id', '').strip()
    if not item_id:
        return redirect('/?tab=inventario&inv_section=checkout')

    for idx, item in enumerate(inventario_items):
        if item.get('id') == item_id:
            item['checked_out'] = False
            item['checkout_state'] = 'retry'
            item['last_checked_out'] = None
            # Enviar al final para volver a preguntarlo cuando termine el resto.
            inventario_items.append(inventario_items.pop(idx))
            guardar_datos()
            break

    return redirect('/?tab=inventario&inv_section=checkout')

@app.route('/inventario/eliminar', methods=['POST'])
def inventario_eliminar():
    item_id = request.form.get('id', '').strip()
    if not item_id:
        return redirect('/?tab=inventario')

    inventario_items[:] = [item for item in inventario_items if item.get('id') != item_id]
    guardar_datos()

    return redirect('/?tab=inventario')

@app.route('/inventario/reiniciar', methods=['POST'])
def inventario_reiniciar():
    inventario_items.clear()
    guardar_datos()

    return redirect('/?tab=inventario')

@app.route('/inventario/reiniciar_checkout', methods=['POST'])
def inventario_reiniciar_checkout():
    for item in inventario_items:
        item['checked_out'] = False
        item['checkout_state'] = 'pending'
        item['last_checked_out'] = None

    guardar_datos()
    return redirect('/?tab=inventario&inv_section=checkout')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)