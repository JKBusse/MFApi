from flask import Flask, jsonify, request, abort, render_template, redirect
import sqlite3
import secrets
import string
import time

app = Flask(__name__)
mfaDatabase = "mfa1.db"

@app.route('/api/apiRegistration', methods=['GET']) #http://localhost:8000/api/apiRegistration?vin=WVWZZZ9NZ6Y104505&carBrand=Volkswagen&carModel=Polo%209N3&carModelYear=2006&carColor=Silver&carEngineCode=AXR&carFuelType=Diesel Beispielaufruf für die Registrierung
def apiRegistration():

    if len(request.args) == 0:
        abort(404)

    if len(request.args.get('vin')) == 0:
        abort(404)

    print("Arguments: ", len(request.args.get('vin')))
    vin = request.args.get('vin')
    brand = request.args.get('carBrand')
    model = request.args.get('carModel')
    modelYear = request.args.get('carModelYear')
    color = request.args.get('carColor')
    engineCode = request.args.get('carEngineCode')
    carFuelType = request.args.get('carFuelType')


    print("VIN Lenght: ", len(vin))
    if vin == "":
        print("VIN darf nicht Leer sein.")
        abort(400)
    if len(vin) != 17:
        print("VIN muss 17 Stellen haben.")
        abort(400)
    
    connection = sqlite3.connect(mfaDatabase)
    cursor = connection.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{vin}'")

    if cursor.fetchone():
        print(f'Die Tabelle "{vin}" existiert bereits.')
        connection.close()
        abort(418) 
    else:
        print(f'Die Tabelle "{vin}" existiert nicht und wird erstellt.') 
        newApiKey = generate_api_key()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {vin} (id INTEGER PRIMARY KEY, vin TEXT, apiKey TEXT, brand TEXT DEFAULT "{brand}", model TEXT DEFAULT "{model}", modelYear INTEGER DEFAULT "{modelYear}", color TEXT DEFAULT "{color}", engineCode TEXT DEFUALT "{engineCode}", fuelLevel INTEGER, fuelType TEXT DEFAULT "{carFuelType}", range INTEGER, lockState TEXT, outsideTemperature INTEGER, fuelConsumption REAL, timestamp TEXT)')
        cursor.execute(f'INSERT INTO {vin} (vin, apiKey, timestamp) VALUES (?, ?, ?)', (vin, newApiKey, time.time()))
        connection.commit() 

    cursor.execute(f'SELECT * FROM {vin}')
    rows = cursor.fetchall()

    for row in rows:
        print(row)
    cursor.execute(f'SELECT * FROM {vin} ORDER BY id DESC LIMIT 1')
    resultDatabase = cursor.fetchone()
    print(resultDatabase)
    connection.close()
    return jsonify(VIN=resultDatabase[1], newApiKey=resultDatabase[2], timestamp=resultDatabase[14]), 201

@app.route('/api/set', methods=['GET']) #http://localhost:8000/api/set?vin=WVWZZZ9NZ6Y104505&carApiKey=4njWzNoCUJUkkZFxL3aBIkcdT9gDKh1v&carBrand=Volkswagen&carModel=Polo%209N3&carModelYear=2006&carColor=Silver&carEngineCode=AXR&carFuelLevel=12&carRange=201&carFuelType=Diesel&carLockState=LOCKED&carOutsideTemperature=-5 Beispielaufruf SET
def apiSet():
    api_key_from_request = request.args.get('carApiKey')
    vin = request.args.get('vin')

    connection = sqlite3.connect(mfaDatabase)
    cursor = connection.cursor()
    cursor.execute(f'SELECT apiKey FROM {vin} ORDER BY apiKey DESC LIMIT 1')
    apiKeyDatabase = cursor.fetchone()
    print(apiKeyDatabase[0])
    print(api_key_from_request)

    if api_key_from_request and api_key_from_request == apiKeyDatabase[0]:
        carApiKey = request.args.get('carApiKey')
        carBrand = request.args.get('carBrand')
        carModel = request.args.get('carModel')
        carModelYear = request.args.get('carModelYear')
        carColor = request.args.get('carColor')
        carEngineCode = request.args.get('carEngineCode')
        carFuelLevel = request.args.get('carFuelLevel')
        carFuelType = request.args.get('carFuelType')
        carRange = request.args.get('carRange')
        carLockState = request.args.get('carLockState')
        carOutsideTemperature = request.args.get('carOutsideTemperature') 
        carFuelConsumption = request.args.get('carFuelConsumption') 

        cursor.execute(f'CREATE TABLE IF NOT EXISTS {vin} (id INTEGER PRIMARY KEY, vin TEXT, apiKey TEXT, brand TEXT, model TEXT, modelYear INTEGER, color TEXT, engineCode TEXT, fuelLevel INTEGER, fuelType TEXT, range INTEGER, lockState TEXT, outsideTemperature INTEGER, fuelConsumption REAL, timestamp TEXT)')
        timeStamp = str(time.time())
        timeStampSplit = timeStamp.split(".")
        cursor.execute(f'INSERT INTO {vin} (vin, apiKey, brand, model, modelYear, color, engineCode, fuelLevel, range, lockState, outsideTemperature, fuelConsumption, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (vin, carApiKey, carBrand, carModel, carModelYear, carColor, carEngineCode, carFuelLevel, carRange, carLockState, carOutsideTemperature, carFuelConsumption, str(timeStampSplit[0])))
        connection.commit()
        cursor.execute(f'SELECT * FROM {vin}')
        rows = cursor.fetchall()

        for row in rows:
            print(row)
    else:
        abort(418)

    connection.close()  
    return '', 200

@app.route('/api/get', methods=['GET']) #http://192.168.2.196:8000/api/get?api_key=4njWzNoCUJUkkZFxL3aBIkcdT9gDKh1v&vin=WVWZZZ9NZ6Y104505 Beispielaufruf GET
def apiGet():
    if request.args.get('api_key') == None:
        abort(404)
    if len(request.args) == 0:
        abort(404)

    if len(request.args.get('api_key')) == 0:
        abort(404)

    if len(request.args.get('vin')) == 0:
        abort(404)
    if request.args.get('api_key') == None:
        abort(400)
    print("len api_key: ", len(request.args.get('api_key')))
    print("len vin: ", len(request.args.get('vin')))
    api_key_from_request = request.args.get('api_key')
    vin = request.args.get('vin')
    print(request.args.get)
    print("VIN Lenght: ", len(vin))
    if vin == "":
        print("VIN darf nicht Leer sein.")
        abort(400)
    if len(vin) != 17:
        print("VIN muss 17 Stellen haben.")
        abort(400)
    
    connection = sqlite3.connect(mfaDatabase)
    cursor = connection.cursor()
    cursor.execute(f'SELECT apiKey FROM {vin} ORDER BY apiKey DESC LIMIT 1')
    apiKeyDatabase = cursor.fetchone()
    #print(apiKeyDatabase[0])
    if api_key_from_request and api_key_from_request == apiKeyDatabase[0]:
        print("API Key akzeptiert.")
        cursor.execute(f'SELECT * FROM {vin} ORDER BY id DESC LIMIT 1')
        resultDatabase = cursor.fetchone()
        print(resultDatabase)
        return jsonify(VIN=resultDatabase[1], brand=resultDatabase[3], model=resultDatabase[4], modelYear=resultDatabase[5], color=resultDatabase[6], engineCode=resultDatabase[7], fuelLevel=resultDatabase[8], fuelType=resultDatabase[9], range=resultDatabase[10], lockState=resultDatabase[11], outsideTemperature=resultDatabase[12], fuelConsumption=resultDatabase[13], timestamp=resultDatabase[14])
    connection.close()
    print("API Key NICHT akzeptiert!")
    abort(418)  

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apiDoku")
def apiDoku():
    return render_template("apiDoku.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/abfrageStart")
def abfrageStart():
    return render_template("abfrageStart.html")

@app.route('/process_form', methods=['POST'])
def process_form():
    vin = request.form.get('vin')
    apiKey = request.form.get('apiKey')
    print("VIN: ", vin)
    # Hier kannst du die erhaltenen Daten weiterverarbeiten
    # Zum Beispiel, speichere sie in einer Datenbank oder mache andere Aktionen
    print('VIN: {vin}, API Key: {apiKey}')
    abfrageString = "/abfrage/" + vin + "/" + apiKey
    return redirect(abfrageString)
    return f'VIN: {vin}, API Key: {apiKey}'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/apiFail")
def apiFail(errorString):
    return render_template('apiFail.html', errorString = errorString)

@app.route('/abfrage/<vin>/<apiKey>')
def abfrage(vin, apiKey):
    api_key_from_request = apiKey

    print("VIN Lenght: ", len(vin))
    if vin == "":
        print("VIN darf nicht Leer sein.")
        abort(400)
    if len(vin) != 17:
        print("VIN muss 17 Stellen haben.")
        abort(400)
    
    connection = sqlite3.connect(mfaDatabase)
    cursor = connection.cursor()
    cursor.execute(f'SELECT apiKey FROM {vin} ORDER BY apiKey DESC LIMIT 1')
    apiKeyDatabase = cursor.fetchone()
    #print(apiKeyDatabase[0])
    if api_key_from_request and api_key_from_request == apiKeyDatabase[0]:
        print("API Key akzeptiert.")
        cursor.execute(f'SELECT * FROM {vin} ORDER BY id DESC LIMIT 1')
        resultDatabase = cursor.fetchone()
        print(resultDatabase)
        return render_template('abfrage.html', VIN=resultDatabase[1], brand=resultDatabase[3], model=resultDatabase[4], modelYear=resultDatabase[5], color=resultDatabase[6], engineCode=resultDatabase[7], fuelLevel=resultDatabase[8], fuelType=resultDatabase[9], range=resultDatabase[10], lockState=resultDatabase[11], outsideTemperature=resultDatabase[12], fuelConsumption=resultDatabase[13], timestamp=resultDatabase[14])
    connection.close()
    print("API Key NICHT akzeptiert!")
    abort(418)  

def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
