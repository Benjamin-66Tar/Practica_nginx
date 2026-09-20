from flask import Flask, jsonify, request
from base import get_cursor

app = Flask(__name__)

@app.route('/api/registro', methods=['POST'])
def registro_usuario():
    try:
        data = request.form if request.form else request.get_json()

        nombre = data.get('nombre')
        edad = data.get('edad')
        correo = data.get('email')

        if not nombre or not edad or not correo:
            return jsonify({'status': 'error', 'message': 'Faltan datos requeridos'}), 400

        with get_cursor() as cursor:
            sql = "INSERT INTO usuarios (nombre, edad, correo) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, edad, correo))

        return jsonify({'status': 'success', 'message': 'Usuario registrado correctamente'}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
