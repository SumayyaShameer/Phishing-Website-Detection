from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model
model = pickle.load(open("model/phishing_model.pkl", "rb"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        features = [float(x) for x in request.form.values()]
        final_features = np.array(features).reshape(1, -1)

        prediction = model.predict(final_features)

        if prediction[0] == 1:
            result = "Legitimate Website ✅"
        else:
            result = "Phishing Website ⚠️"

        return render_template("index.html", prediction_text=result)

    except:
        return render_template(
            "index.html",
            prediction_text="Invalid input. Please enter valid numeric values."
        )

if __name__ == "__main__":
    app.run(debug=True)
