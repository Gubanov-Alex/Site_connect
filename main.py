from flask import Flask, request, jsonify
import waitress

app =Flask (__name__)

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    return jsonify({"message": "Data received", "data": data}), 201



if __name__ == '__main__':
      # app.run(debug=True)
      waitress.serve(app, host='0.0.0.0', port=8080)



