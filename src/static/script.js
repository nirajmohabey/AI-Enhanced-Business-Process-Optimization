document.getElementById('predictionForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    // Get form data
    const taskName = document.getElementById('task_name').value;
    const durationHours = parseFloat(document.getElementById('duration_hours').value);
    const errorRate = parseFloat(document.getElementById('error_rate').value);

    // Prepare request payload
    const payload = {
        task_name: taskName,
        duration_hours: durationHours,
        error_rate: errorRate
    };

    try {
        // Send POST request to Flask API
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to fetch prediction');
        }

        const data = await response.json();

        // Display results
        document.getElementById('predictedCost').textContent = data.predicted_cost.toFixed(2);
        const recommendationsList = document.getElementById('recommendations');
        recommendationsList.innerHTML = data.recommendations
            .split('\n')
            .map(rec => `<li>${rec}</li>`)
            .join('');
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});