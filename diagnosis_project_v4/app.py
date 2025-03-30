from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle

app = Flask(__name__)

# Load model and symptoms (but NOT the label_encoder initially)
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('symptoms.pkl', 'rb') as f:
    symptoms = pickle.load(f)

def predict_disease(symptoms_text):
    try:
        # Load the LabelEncoder here, inside the function
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)

        # Lowercase and clean input
        symptoms_list = [s.strip() for s in symptoms_text.lower().split(',') if s.strip()]
        input_data = [1 if symptom in symptoms_list else 0 for symptom in symptoms]
        input_df = pd.DataFrame([input_data], columns=symptoms)


        # Make predictions
        predicted_class = model.predict(input_df)[0]

        # Try to inverse transform, and refit if needed
        try:
            predicted_disease = label_encoder.inverse_transform([predicted_class])[0]
        except ValueError:
            # Refit Label Encoder, appending only if truly new.
            print("Detected potentially unseen label.  Checking...")
            all_labels = label_encoder.classes_.tolist()  # Get existing labels as a list
            if predicted_class not in all_labels:  # <--- KEY CHECK
                all_labels.append(predicted_class)  # Add the integer
                new_label_enc = LabelEncoder()  # Create a *new* encoder
                new_label_enc.fit(all_labels)  # Fit on the integers
                predicted_disease = new_label_enc.inverse_transform([predicted_class])[0]
                # OVERWRITE the label_encoder.  Important for future predictions.
                with open('label_encoder.pkl', 'wb') as f:
                    pickle.dump(new_label_enc, f)
                label_encoder = new_label_enc# Make sure we use this encoder now
            else:

                predicted_disease = "Unknown Disease"

        probabilities = {}
        if predicted_disease != "Other":
            prediction_prob = model.predict_proba(input_df)[0] * 100
            for i, prob in enumerate(prediction_prob):
                try:
                    disease_name = label_encoder.inverse_transform([i])[0]
                    if disease_name != "Other":
                        probabilities[disease_name] = prob
                except ValueError: #if label is not found.
                    continue

        if predicted_disease == "Other":
            return "Rare Disease (Not in Main Dataset)", {}
        return predicted_disease, probabilities
    except Exception as e:
        print("An error occurred during prediction:", e)
        return "Error", {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    symptoms_text = data['symptoms']
    predicted_disease, probabilities = predict_disease(symptoms_text)

    return jsonify({
        'prediction': predicted_disease,
        'probabilities': probabilities
    })

if __name__ == '__main__':
    app.run(debug=True)
