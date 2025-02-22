from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista de casos ficticios con más detalle
casos = [
    {
        "id": 1,
        "titulo": "El Caso del Mango Robado",
        "hechos": "Juan acusa a María de robarle un mango de su árbol el 5 de febrero en Villa Mella. María sostiene que el mango cayó solo y ella lo recogió para consumirlo.",
        "pruebas": {"Huellas en el patio": 8, "Foto borrosa de María cerca del árbol": 3},
        "testigos": {"Vecino Juan (vio a María trepada)": 6, "Vecino Pedro (el árbol estaba podrido)": 4},
        "defensa": "María sostiene que no hubo hurto porque el mango ya estaba en el suelo.",
        "ley": "Código Penal RD, Art. 379 (Hurto): Pena de 3 meses a 1 año o multa.",
        "procedimiento": "Código Procesal Penal RD, Art. 169: La admisibilidad de las pruebas debe ser demostrada por el Fiscal.",
        "condiciones_ganadoras": {
            "Fiscal": ["art. 379", "hurto", "huellas"],
            "Abogado Defensor": ["cayó", "vecino pedro"]
        }
    },
    {
        "id": 2,
        "titulo": "El Vecino Ruidoso",
        "hechos": "Pedro, un músico de Los Mina, reproduce música a alto volumen todas las noches desde hace 3 meses. Ana, su vecina, lo demanda por perturbar su descanso.",
        "pruebas": {"Grabación del ruido (80 dB)": 7, "Queja formal de Ana en el ayuntamiento": 5},
        "testigos": {"Vecina Ana (no puede dormir)": 6, "Vecino Luis (el ruido no le molesta)": 4},
        "defensa": "Pedro sostiene que el volumen de la música no excede los límites legales y que es su fuente de ingresos.",
        "ley": "Ley 64-00, Art. 118 (Contaminación Sónica): Multa de 1 a 10 salarios mínimos.",
        "procedimiento": "Código Procesal Penal RD, Art. 265: La querella debe presentarse dentro de los 6 meses del hecho.",
        "condiciones_ganadoras": {
            "Fiscal": ["ley 64-00", "grabación", "80 db"],
            "Abogado Defensor": ["no pasa", "vecino luis"]
        }
    },
    {
        "id": 3,
        "titulo": "El Motoconcho Estafador",
        "hechos": "Ramón, un motociclista de Santo Domingo Este, solicitó un préstamo de 50,000 DOP a Carmen para comprar una motocicleta nueva, prometiendo devolverlo en 3 meses con intereses. Carmen afirma que Ramón no pagó y desapareció. Ramón asegura que pagó la totalidad en efectivo a un primo de Carmen, pero no tiene recibo. Un mes después, Carmen vio a Ramón con una motocicleta nueva.",
        "pruebas": {
            "Contrato verbal grabado en un audio de WhatsApp": 7,
            "Foto de Ramón con una motocicleta nueva": 4,
            "Denuncia de Carmen en el destacamento": 5
        },
        "testigos": {
            "Carmen (la víctima)": 6,
            "Primo José (supuesto receptor del pago)": 5,
            "Vecino Miguel (vio a Ramón con efectivo)": 3
        },
        "defensa": "Ramón asegura que pagó al primo José en efectivo y que Carmen miente para obtener más dinero.",
        "ley": "Código Penal RD, Art. 405 (Estafa): Pena de 6 meses a 2 años y multa.",
        "procedimiento": "Código Procesal Penal RD, Art. 172: El audio debe ser autenticado para ser admisible como prueba.",
        "condiciones_ganadoras": {
            "Fiscal": ["art. 405", "audio", "estafa"],
            "Abogado Defensor": ["primo josé", "no estafa"]
        }
    }
]

# Página principal
@app.route('/')
def inicio():
    return render_template('inicio.html', casos=casos)

# Página de caso
@app.route('/caso/<int:caso_id>', methods=['GET', 'POST'])
def caso(caso_id):
    caso = next((c for c in casos if c['id'] == caso_id), None)
    if not caso:
        return "Caso no encontrado", 404
    
    if request.method == 'POST':
        argumento = request.form['argumento'].lower()
        rol = request.form['rol']
        puntos = 0
        feedback = []

        # Estructura legal
        if "art." in argumento or "ley" in argumento:
            puntos += 10
            feedback.append("Correcto: Ha citado una ley.")
        if any(p in argumento for p in caso["pruebas"].keys()) or any(t in argumento for t in caso["testigos"].keys()):
            puntos += 5
            feedback.append("Correcto: Ha utilizado pruebas o testigos.")
        if "pido" in argumento or "solicito" in argumento or "niego" in argumento:
            puntos += 5
            feedback.append("Correcto: Ha incluido una conclusión legal.")

        # Ponderar pruebas y testigos
        for prueba, peso in caso["pruebas"].items():
            if prueba.lower() in argumento:
                puntos += peso
                feedback.append(f"Uso adecuado de '{prueba}' (+{peso} puntos).")
        for testigo, peso in caso["testigos"].items():
            if testigo.lower() in argumento:
                puntos += peso
                feedback.append(f"Uso adecuado de '{testigo}' (+{peso} puntos).")

        # Coherencia con el rol y condiciones ganadoras
        condiciones = caso["condiciones_ganadoras"][rol]
        if rol == "Fiscal":
            if any(c in argumento for c in condiciones):
                puntos += 5
                feedback.append("Coherente: Ha presentado una acusación adecuada como Fiscal.")
            if "no hubo" in argumento or "inocente" in argumento:
                puntos -= 5
                feedback.append("Error: Como Fiscal, no puede defender al acusado.")
        elif rol == "Abogado Defensor":
            if any(c in argumento for c in condiciones):
                puntos += 5
                feedback.append("Coherente: Ha presentado una defensa adecuada como Abogado Defensor.")
            if "culpable" in argumento or "pena" in argumento:
                puntos -= 5
                feedback.append("Error: Como Abogado Defensor, no puede acusar al defendido.")

        # Penalizar errores o vaguedad
        if not any(word in argumento for word in ["hurto", "cayó", "ruido", "grabación", "testigo", "ley", "art.", "estafa", "audio", "pago"]):
            puntos -= 5
            feedback.append("Incorrecto: El argumento carece de sustancia legal.")

        # Resultado y feedback
        if puntos >= 20:
            resultado = f"¡Éxito! Puntos: {puntos}. El juez concluye: ‘Argumento sólido y bien fundamentado.’"
        elif puntos >= 10:
            resultado = f"Resultado neutro. Puntos: {puntos}. El juez concluye: ‘Argumento aceptable, pero requiere mayor fundamentación.’"
        else:
            resultado = f"Fallo. Puntos: {puntos}. El juez concluye: ‘Argumento insuficiente, reconsiderar su enfoque.’"
        
        resultado += "<br><br>Detalles:<br>" + "<br>".join(feedback)

        return render_template('caso.html', caso=caso, resultado=resultado)
    
    return render_template('caso.html', caso=caso)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)