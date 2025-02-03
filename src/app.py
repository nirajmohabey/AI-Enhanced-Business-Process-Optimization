import os
import logging
import pandas as pd
import pickle
from flask import Flask, request, jsonify, render_template
from llm import RecommendationGenerator  # Ensure this imports the correct function

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    filename='logs/api.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load the trained model and column names
MODEL_FILE = 'C:/Users/nmoha/Projects/AI-Enhanced Business Process Optimization/src/trained_model.pkl'

def load_model():
    """Load the trained model and column names from the pickle file."""
    try:
        with open(MODEL_FILE, 'rb') as file:
            model_data = pickle.load(file)
            model = model_data['model']
            column_names = model_data['column_names']
        logging.info('Model and column names loaded successfully.')
        return model, column_names
    except Exception as e:
        logging.error(f'Error loading model: {e}')
        raise

model, column_names = load_model()

@app.route('/')
def home():
    """Serve the front-end HTML page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict cost and generate recommendations based on input data."""
    try:
        # Get input data from the request
        task_name = request.json.get('task_name')
        duration_hours = request.json.get('duration_hours')
        error_rate = request.json.get('error_rate')

        logging.info(f'Input Data - Task: {task_name}, Duration: {duration_hours}, Error Rate: {error_rate}')

        # Prepare input for prediction
        input_data = pd.DataFrame([[duration_hours, error_rate, task_name]],
                                  columns=['Duration_Hours', 'Error_Rate', 'Task_Name'])

        # One-hot encode Task_Name
        input_data = pd.get_dummies(input_data, columns=['Task_Name'], drop_first=True)

        # Ensure all expected columns are present
        for col in column_names:
            if col not in input_data.columns:
                input_data[col] = 0  # Add missing columns with value 0

        # Ensure the input data is ordered the same way as the model was trained
        input_data = input_data[column_names]

        logging.info(f'Processed Input Data:\n{input_data}')

        # Make prediction
        predicted_cost = model.predict(input_data)[0]
        logging.info(f'Predicted Cost: {predicted_cost}')

        # Generate recommendations
        recommender = RecommendationGenerator(model_file=MODEL_FILE)
        recommendations = recommender.generate_recommendation(task_name=task_name, predicted_cost=predicted_cost)

        logging.info(f'Recommendations: {recommendations}')

        # Return the prediction and recommendations as JSON
        return jsonify({
            'predicted_cost': predicted_cost,
            'recommendations': recommendations
        }), 200

    except Exception as e:
        logging.error(f'Error during prediction: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Run the Flask app
    app.run(debug=True)