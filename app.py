from flask import Flask, request, render_template, redirect, jsonify
import json, os
from datetime import datetime, timedelta

app = Flask(__name__)
data_file = 'pilas.json'
config_file = 'config.json'
battery_names_file = 'battery_names.json'

# Cargar configuración
def load_config():
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {'competition_mode': None}
    return {'competition_mode': None}

def save_config(config):
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# Cargar nombres de baterías desde JSON
def load_battery_names():
    if os.path.exists(battery_names_file):
        try:
            with open(battery_names_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Si hay error, usar valores por defecto
            return {
                "FRC": ["Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird",
                       "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
                       "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                "FTC": ["Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird",
                       "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
                       "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            }
    return {
        "FRC": ["Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird",
               "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
               "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        "FTC": ["Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird",
               "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
               "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    }

# Cargar configuración y nombres
config = load_config()
battery_names_data = load_battery_names()

# Obtener nombres según el modo de competencia
def get_nombres_fijos():
    mode = config.get('competition_mode')
    if mode == 'FTC':
        return battery_names_data.get('FTC', [])
    elif mode == 'FRC':
        return battery_names_data.get('FRC', [])
    else:
        # Por defecto, usar FRC si no hay modo configurado
        return battery_names_data.get('FRC', [])

# Obtener tiempo de cooldown según el modo (en segundos)
def get_cooldown_time():
    mode = config.get('competition_mode')
    if mode == 'FTC':
        return 900  # 15 minutos
    else:  # FRC o default
        return 1800  # 30 minutos

def es_pila_lista_para_conectar(nombre):
    """Verifica si una pila está lista para conectar"""
    # Si no tiene datos, está lista para conectar
    pila = next((p for p in pilas if p['nombre'] == nombre), None)
    if not pila:
        return True

    # Si está en cooldown, verificar si han pasado el tiempo según el modo
    if nombre in pilas_en_cooldown:
        timestamp_cooldown = datetime.strptime(pilas_en_cooldown[nombre], "%Y-%m-%d %H:%M")
        tiempo_transcurrido = datetime.now() - timestamp_cooldown
        cooldown_seconds = get_cooldown_time()
        return tiempo_transcurrido.total_seconds() >= cooldown_seconds

    return False

def obtener_pilas_listas_para_conectar():
    """Obtiene lista de pilas listas para conectar ordenadas por tiempo sin conectar"""
    global pilas_en_cooldown, pilas_inhabilitadas
    pilas_listas = []
    cooldowns_a_limpiar = []
    nombres_fijos = get_nombres_fijos()
    cooldown_seconds = get_cooldown_time()

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

                # Si ya pasó el tiempo de cooldown, marcar para limpiar
                if tiempo_transcurrido.total_seconds() >= cooldown_seconds:
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
        data_to_save = {
            'pilas': pilas,
            'pilas_en_uso': pilas_en_uso,
            'pilas_en_cooldown': pilas_en_cooldown
        }
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False)
    
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
# Nota: mantenemos compatibilidad con el formato antiguo que usaba 'pila_en_uso'
if os.path.exists(data_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
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
    except json.JSONDecodeError:
        pilas = []

@app.route('/')
def index():
    # Siempre redirigir a la selección de modo
    return redirect('/select_mode')

@app.route('/select_mode')
def select_mode():
    return render_template('select_mode.html')

@app.route('/main')
def main():
    # Verificar que haya un modo seleccionado
    if config.get('competition_mode') is None:
        return redirect('/select_mode')

    # Crear lista completa para mostrar
    listado = []
    nombres_fijos = get_nombres_fijos()
    for nombre in nombres_fijos:
        pila = next((p for p in pilas if p['nombre'] == nombre), None)
        if pila:
            listado.append(pila)
        else:
            listado.append({"nombre": nombre, "carga": "Sin datos", "ohms": "Sin datos"})

    # Ordenar por Carga (mayor a menor) y luego por Ohms (menor a mayor)
    def key_ordenamiento(p):
        try:
            carga = float(p['carga'])
        except:
            # "Sin datos" se coloca al final con carga muy baja
            return (-1, 999999)
        
        try:
            ohms = float(p['ohms'])
        except:
            # Si no hay ohms válidos, usar valor alto para que vaya al final del grupo de misma carga
            ohms = 999999
        
        # Retornar tupla: (carga negativa para orden descendente, ohms para orden ascendente)
        return (-carga, ohms)
    
    listado_ordenado = sorted(listado, key=key_ordenamiento)

    # Calcular próximo chequeo si hay última actualización
    proximo_chequeo = None
    if ultima_actualizacion:
        try:
            # Convertir la fecha de string a datetime y sumar el tiempo de cooldown
            fecha_actualizacion = datetime.strptime(ultima_actualizacion, "%Y-%m-%d %H:%M")
            cooldown_minutes = get_cooldown_time() // 60
            proximo = fecha_actualizacion + timedelta(minutes=cooldown_minutes)
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

    return render_template('index.html',
                         pilas=listado_ordenado,
                         ultima_actualizacion=ultima_actualizacion,
                         proximo_chequeo=proximo_chequeo,
                         pilas_en_uso=pilas_en_uso,
                         pilas_en_cooldown=pilas_en_cooldown,
                         pilas_listas=pilas_listas,
                         mejor_pila=mejor_pila,
                         pilas_inhabilitadas=list(pilas_inhabilitadas),
                         competition_mode=config.get('competition_mode'),
                         nombres_fijos=get_nombres_fijos(),
                         cooldown_minutes=get_cooldown_time()//60)

@app.route('/agregar', methods=['POST'])
def agregar():
    global ultima_actualizacion

    nombre = request.form['nombre']
    mode = config.get('competition_mode')

    # Para FTC, solo necesitamos el nombre (sin carga ni ohms)
    if mode == 'FTC':
        pila_data = {"nombre": nombre, "carga": "N/A", "ohms": "N/A"}
    else:  # FRC o default
        carga = request.form['carga']
        ohms = request.form['ohms']
        pila_data = {"nombre": nombre, "carga": carga, "ohms": ohms}

    # Reemplazar si ya existe
    encontrado = False
    for i, pila in enumerate(pilas):
        if pila['nombre'] == nombre:
            pilas[i] = pila_data
            encontrado = True
            break
    if not encontrado:
        pilas.append(pila_data)

    # Guardar en JSON con nuevo formato
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas)
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    # Guardar fecha y hora de actualización
    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")

    return redirect('/main')

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
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas)
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')


@app.route('/toggle_inhabilitar', methods=['POST'])
def toggle_inhabilitar():
    global pilas_inhabilitadas
    nombre = request.form.get('nombre')
    if not nombre:
        return redirect('/main')

    if nombre in pilas_inhabilitadas:
        pilas_inhabilitadas.remove(nombre)
    else:
        pilas_inhabilitadas.add(nombre)

    # Guardar cambios
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas)
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')

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
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas)
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global pilas, pilas_en_uso, pilas_en_cooldown, ultima_actualizacion

    # Reiniciar todas las variables globales
    pilas = []
    pilas_en_uso = []
    pilas_en_cooldown = {}
    ultima_actualizacion = None

    # Guardar el estado limpio en JSON
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas)
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')

@app.route('/set_mode', methods=['POST'])
def set_mode():
    global config, battery_names_data
    mode = request.form.get('mode')
    if mode in ['FTC', 'FRC']:
        config['competition_mode'] = mode
        save_config(config)
        # Reload battery names data after mode change
        battery_names_data = load_battery_names()
    return redirect('/main')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
