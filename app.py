from flask import Flask, request, render_template, redirect, jsonify
import json, os, webbrowser, threading
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

def get_cooldown_time():
    mode = config.get('competition_mode')
    if mode == 'FTC':
        return 900  
    else:  
        return 1800 

def es_pila_lista_para_conectar(nombre):
    """Verifica si una pila está lista para conectar"""
    # Si no tiene datos, está lista para conectar
    pila = next((p for p in pilas if p['nombre'] == nombre), None)
    if not pila:
        return True

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
            continue  
            
        if es_pila_lista_para_conectar(nombre):
            tiempo_sin_conectar = None
            
            if nombre in pilas_en_cooldown:
                timestamp_cooldown = datetime.strptime(pilas_en_cooldown[nombre], "%Y-%m-%d %H:%M")
                tiempo_transcurrido = datetime.now() - timestamp_cooldown

                if tiempo_transcurrido.total_seconds() >= cooldown_seconds:
                    cooldowns_a_limpiar.append(nombre)
                    tiempo_sin_conectar = timestamp_cooldown
                else:
                    continue 
            else:
                tiempo_sin_conectar = datetime(2000, 1, 1)
            
            pilas_listas.append({
                'nombre': nombre,
                'tiempo_sin_conectar': tiempo_sin_conectar,
                'disabled': (nombre in pilas_inhabilitadas)
            })
    
    for nombre in cooldowns_a_limpiar:
        del pilas_en_cooldown[nombre]
    
    if cooldowns_a_limpiar:
        data_to_save = {
            'pilas': pilas,
            'pilas_en_uso': pilas_en_uso,
            'pilas_en_cooldown': pilas_en_cooldown
        }
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False)
    
    pilas_listas.sort(key=lambda x: (x.get('disabled', False), x['tiempo_sin_conectar']))
    
    return pilas_listas

pilas = []
ultima_actualizacion = None 
pilas_en_uso = []  
pilas_en_cooldown = {}
pilas_inhabilitadas = set()
pilas_timestamps = {}
if os.path.exists(data_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                pilas = data
            else:
                pilas = data.get('pilas', [])
                if 'pilas_en_uso' in data:
                    pilas_en_uso = data.get('pilas_en_uso') or []
                else:
                    single = data.get('pila_en_uso', None)
                    pilas_en_uso = [single] if single else []
                pilas_en_cooldown = data.get('pilas_en_cooldown', {})
                pilas_inhabilitadas = set(data.get('pilas_inhabilitadas', []) or [])
                pilas_timestamps = data.get('pilas_timestamps', {})
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

    proximo_chequeo = None
    if ultima_actualizacion:
        try:
            fecha_actualizacion = datetime.strptime(ultima_actualizacion, "%Y-%m-%d %H:%M")
            cooldown_minutes = get_cooldown_time() // 60
            proximo = fecha_actualizacion + timedelta(minutes=cooldown_minutes)
            proximo_chequeo = proximo.strftime("%H:%M")
        except:
            proximo_chequeo = None

    pilas_listas = obtener_pilas_listas_para_conectar()

    mejor_pila = None
    for p in listado_ordenado:
        try:
            if p.get('carga') != 'Sin datos' and p.get('nombre') not in pilas_en_uso and p.get('nombre') not in pilas_en_cooldown:
                mejor_pila = p.get('nombre')
                break
        except Exception:
            continue

    tiempos_restantes = {}
    cooldown_seconds = get_cooldown_time()
    for nombre, timestamp_str in pilas_en_cooldown.items():
        try:
            timestamp_cooldown = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            tiempo_transcurrido = datetime.now() - timestamp_cooldown
            tiempo_restante_segundos = cooldown_seconds - tiempo_transcurrido.total_seconds()
            
            if tiempo_restante_segundos > 0:
                tiempo_restante_minutos = int(tiempo_restante_segundos / 60) + (1 if tiempo_restante_segundos % 60 > 0 else 0)
                tiempos_restantes[nombre] = tiempo_restante_minutos
            else:
                tiempos_restantes[nombre] = 0
        except Exception:
            tiempos_restantes[nombre] = 0
    
    tiempos_transcurridos = {}
    for nombre, timestamp_str in pilas_timestamps.items():
        try:
            timestamp_registro = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            tiempo_desde_registro = datetime.now() - timestamp_registro
            # Convertir a minutos
            minutos_transcurridos = int(tiempo_desde_registro.total_seconds() / 60)
            tiempos_transcurridos[nombre] = minutos_transcurridos
        except Exception:
            tiempos_transcurridos[nombre] = 0

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
                         cooldown_minutes=get_cooldown_time()//60,
                         tiempos_restantes=tiempos_restantes,
                         tiempos_transcurridos=tiempos_transcurridos)

@app.route('/agregar', methods=['POST'])
def agregar():
    global ultima_actualizacion, pilas_timestamps

    nombre = request.form['nombre']
    
    # "Cargar Pila" solo registra el nombre y comienza el timer
    # No importa el modo - siempre N/A hasta que se registre
    pila_data = {"nombre": nombre, "carga": "N/A", "ohms": "N/A"}

    # Reemplazar si ya existe
    encontrado = False
    for i, pila in enumerate(pilas):
        if pila['nombre'] == nombre:
            pilas[i] = pila_data
            encontrado = True
            break
    if not encontrado:
        pilas.append(pila_data)
    
    # Registrar timestamp de cuando se agregó/actualizó la pila
    pilas_timestamps[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Guardar en JSON con nuevo formato
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")

    return redirect('/main')

@app.route('/registrar', methods=['POST'])
def registrar():
    global ultima_actualizacion

    nombre = request.form['nombre']
    carga = request.form['carga']
    ohms = request.form['ohms']
    
    pila_data = {"nombre": nombre, "carga": carga, "ohms": ohms}

    encontrado = False
    for i, pila in enumerate(pilas):
        if pila['nombre'] == nombre:
            pilas[i] = pila_data
            encontrado = True
            break
    if not encontrado:
        pilas.append(pila_data)
        if nombre not in pilas_timestamps:
            pilas_timestamps[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M")

    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")

    return redirect('/main')

@app.route('/pila_en_uso', methods=['POST'])
def marcar_pila_en_uso():
    global pilas_en_uso, pilas_timestamps

    nombre = request.form['nombre']
    if nombre not in pilas_en_uso:
        pilas_en_uso.append(nombre)

    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]
    
    if nombre in pilas_timestamps:
        del pilas_timestamps[nombre]

    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
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

    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')

@app.route('/recibir_pila', methods=['POST'])
def recibir_pila():
    global pilas_en_cooldown, pilas_timestamps
    
    nombre = request.form['nombre']
    
    global pilas_en_uso
    try:
        if nombre in pilas_en_uso:
            pilas_en_uso = [p for p in pilas_en_uso if p != nombre]
    except Exception:
        pilas_en_uso = []
    
    # Borrar los datos de la pila si existen
    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]
    
    if nombre in pilas_timestamps:
        del pilas_timestamps[nombre]
    
    pilas_en_cooldown[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Guardar en JSON con nuevo formato
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
    }
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False)

    return redirect('/main')

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global pilas, pilas_en_uso, pilas_en_cooldown, ultima_actualizacion, pilas_timestamps

    # Reiniciar todas las variables globales
    pilas = []
    pilas_en_uso = []
    pilas_en_cooldown = {}
    pilas_timestamps = {}
    ultima_actualizacion = None

    # Guardar el estado limpio en JSON
    data_to_save = {
        'pilas': pilas,
        'pilas_en_uso': pilas_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown,
        'pilas_inhabilitadas': list(pilas_inhabilitadas),
        'pilas_timestamps': pilas_timestamps
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
    # Función para abrir el navegador automáticamente
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000/')
    
    # Abrir el navegador después de 1.5 segundos (dar tiempo a que Flask inicie)
    threading.Timer(1.5, open_browser).start()
    
    # Iniciar el servidor Flask
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)

