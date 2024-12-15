from flask import Flask, request, jsonify
from lib.parser import parseText
import os
import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

ENDPOINT = os.environ.get('ENDPOINT')

with open('data.json', 'r') as file:
    data = json.load(file)

@app.route('/rutas', methods=['POST'])

def rutas():
    params = request.get_json()

    ciudad_origen = params.get("ciudad_origen", "").ljust(4, '0')
    ciudad_destino = params.get("ciudad_destino", "").ljust(4, '0')

    estado_origen = data['puntos'][ciudad_origen]['estado']
    estado_destino = data['puntos'][ciudad_destino]['estado']

    vehiculos = params.get("vehiculos", 1)
    calcula_rendimiento = 'si' if params.get("calcula_rendimiento") == 'true' else None
    tamanio_vehiculo = params.get("tamanio_vehiculo", 2)
    rendimiento = params.get("rendimiento", 2.9)
    combustible = params.get("combustible", 24)

    zonas_urbanas = params.get("zonas_urbanas", 'false') == 'true'

    query = {
        'action': 'cmdSolRutas',
        'tipo': 1,
        'red': 'detallada',
        'edoOrigen': estado_origen,
        'ciudadOrigen': ciudad_origen,
        'edoDestino': estado_destino,
        'ciudadDestino': ciudad_destino,
        'vehiculos': vehiculos,
        'calculaRendimiento': calcula_rendimiento,
        'tamanioVehiculo': tamanio_vehiculo,
        'rendimiento': rendimiento,
        'combustible': combustible
    }

    res = requests.get(ENDPOINT if ENDPOINT else "", params=query).text

    html = BeautifulSoup(res, 'html.parser')
    all_tr = (html.find_all('tr'))

    ruta = all_tr[1].find('td').text.strip()
    ruta = parseText(ruta)

    combustible_estimado = (all_tr[-7].find_all('td'))[-1].text
    combustible_estimado = parseText(combustible_estimado)

    tarifa_mas_combustible = (all_tr[-5].find_all('td'))[-1].text
    tarifa_mas_combustible = parseText(tarifa_mas_combustible)

    totales = (all_tr[-9].find_all('td'))
    totales_data = {
        "long(km)": parseText(totales[1].text),
        "tiempo(hrs)": parseText(totales[2].text),
        "tarifa_casetas": parseText(totales[-1].text),
        "tarifa_casetas_mas_combustible": tarifa_mas_combustible,
        "costo_combustible": combustible_estimado
    }

    rutas_data = []

    headers = ['nombre', 'estado', 'carretera', 'long(km)', 'tiempo(hrs)', 'caseta', 'costo_caseta']

    for tr in all_tr[5: -10]:
        all_td = tr.find_all('td')
        if all_td:  
            route_data = {headers[i]: parseText(all_td[i].text) for i in range(len(all_td))}
            rutas_data.append(route_data)

    return jsonify({
        "status": "200",
        "ruta": ruta,
        "totales": totales_data,
        "rutas": rutas_data
    })

if __name__ == '__main__':
    app.run(debug=True)
