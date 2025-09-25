#!/usr/bin/env python3
"""
OverPilas Desktop Launcher
Launches the Flask app and opens the default browser automatically.
"""

import os
import sys
import time
import threading
import webbrowser
from flask import Flask, request, render_template, redirect
import json
from datetime import datetime, timedelta

# Get the directory where this script is located
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    bundle_dir = getattr(sys, '_MEIPASS', application_path)
    template_dir = os.path.join(bundle_dir, 'templates')
    static_dir = os.path.join(bundle_dir, 'static')
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))
    bundle_dir = application_path
    template_dir = os.path.join(application_path, 'templates')
    static_dir = os.path.join(application_path, 'static')

# Change to the application directory (for data files like pilas.json)
os.chdir(application_path)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
data_file = 'pilas.json'

# Lista fija de nombres
nombres_fijos = ["Tlacua", "Jasper", "Caditos", "Timmy", "Thunderbird", 
                "Miguelito", "Cesarín", "El tío", "Chopper", "Gaia", "Gipsy",
                "1", "2", "3", "4", "5", "6", "7", "8", "9"]

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
    global pilas_en_cooldown
    pilas_listas = []
    cooldowns_a_limpiar = []
    
    for nombre in nombres_fijos:
        if nombre == pila_en_uso:
            continue  # Saltar pila en uso
            
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
                'tiempo_sin_conectar': tiempo_sin_conectar
            })
    
    # Limpiar cooldowns que ya completaron los 30 minutos
    for nombre in cooldowns_a_limpiar:
        del pilas_en_cooldown[nombre]
    
    # Si se limpiaron cooldowns, guardar los cambios
    if cooldowns_a_limpiar:
        data_to_save = {
            'pilas': pilas,
            'pila_en_uso': pila_en_uso,
            'pilas_en_cooldown': pilas_en_cooldown
        }
        with open(data_file, 'w') as f:
            json.dump(data_to_save, f)
    
    # Ordenar por tiempo sin conectar (más antiguos primero)
    pilas_listas.sort(key=lambda x: x['tiempo_sin_conectar'])
    
    return pilas_listas

# Cargar datos existentes de forma segura
pilas = []
ultima_actualizacion = None  # Guardará la fecha y hora
pila_en_uso = None  # Guardará el nombre de la pila en uso
pilas_en_cooldown = {}  # Guardará {nombre: timestamp} de pilas en cooldown
if os.path.exists(data_file):
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                # Formato anterior - solo lista de pilas
                pilas = data
            else:
                # Formato nuevo - objeto con pilas, pila_en_uso y cooldowns
                pilas = data.get('pilas', [])
                pila_en_uso = data.get('pila_en_uso', None)
                pilas_en_cooldown = data.get('pilas_en_cooldown', {})
    except json.JSONDecodeError:
        pilas = []

@app.route('/')
def index():
    # Crear lista completa para mostrar
    listado = []
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
            # Convertir la fecha de string a datetime y sumar 30 minutos
            fecha_actualizacion = datetime.strptime(ultima_actualizacion, "%Y-%m-%d %H:%M")
            proximo = fecha_actualizacion + timedelta(minutes=30)
            proximo_chequeo = proximo.strftime("%H:%M")
        except:
            proximo_chequeo = None

    # Obtener pilas listas para conectar
    pilas_listas = obtener_pilas_listas_para_conectar()

    return render_template('index.html', pilas=listado_ordenado, ultima_actualizacion=ultima_actualizacion, proximo_chequeo=proximo_chequeo, pila_en_uso=pila_en_uso, pilas_en_cooldown=pilas_en_cooldown, pilas_listas=pilas_listas)

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
    data_to_save = {
        'pilas': pilas,
        'pila_en_uso': pila_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown
    }
    with open(data_file, 'w') as f:
        json.dump(data_to_save, f)

    # Guardar fecha y hora de actualización
    ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")

    return redirect('/')

@app.route('/pila_en_uso', methods=['POST'])
def marcar_pila_en_uso():
    global pila_en_uso
    
    nombre = request.form['nombre']
    pila_en_uso = nombre
    
    # Borrar los datos de la pila seleccionada
    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]
    
    # Guardar en JSON con nuevo formato
    data_to_save = {
        'pilas': pilas,
        'pila_en_uso': pila_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown
    }
    with open(data_file, 'w') as f:
        json.dump(data_to_save, f)
    
    return redirect('/')

@app.route('/recibir_pila', methods=['POST'])
def recibir_pila():
    global pilas_en_cooldown
    
    nombre = request.form['nombre']
    
    # Remover de pila_en_uso si era la que estaba en uso
    global pila_en_uso
    if pila_en_uso == nombre:
        pila_en_uso = None
    
    # Borrar los datos de la pila si existen
    pilas[:] = [pila for pila in pilas if pila['nombre'] != nombre]
    
    # Marcar como en cooldown con timestamp actual
    pilas_en_cooldown[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Guardar en JSON con nuevo formato
    data_to_save = {
        'pilas': pilas,
        'pila_en_uso': pila_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown
    }
    with open(data_file, 'w') as f:
        json.dump(data_to_save, f)
    
    return redirect('/')

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global pilas, pila_en_uso, pilas_en_cooldown, ultima_actualizacion
    
    # Reiniciar todas las variables globales
    pilas = []
    pila_en_uso = None
    pilas_en_cooldown = {}
    ultima_actualizacion = None
    
    # Guardar el estado limpio en JSON
    data_to_save = {
        'pilas': pilas,
        'pila_en_uso': pila_en_uso,
        'pilas_en_cooldown': pilas_en_cooldown
    }
    with open(data_file, 'w') as f:
        json.dump(data_to_save, f)
    
    return redirect('/')

def open_browser():
    """Open the default browser after a short delay"""
    time.sleep(1.5)  # Wait for Flask to start
    webbrowser.open('http://127.0.0.1:5000')

def main():
    print("🔋 Starting OverPilas Application...")
    print("📍 Application directory:", application_path)
    print("🌐 Opening browser at http://127.0.0.1:5000")
    print("⚠️  Close this window to stop the application")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to close...")

if __name__ == '__main__':
    main()