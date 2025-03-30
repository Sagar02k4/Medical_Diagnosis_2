// static/js/script.js
function submitSymptoms() {
    const symptomInput = document.getElementById('symptomInput').value;
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms: symptomInput }),
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `<h2>Predicted Disease:</h2><p>${data.prediction}</p>`;

        if (data.probabilities) {
            const probList = document.createElement('ul');
            for (const disease in data.probabilities) {
                const listItem = document.createElement('li');
                // Check if it's a number BEFORE calling toFixed()
                if (typeof data.probabilities[disease] === 'number') {
                    listItem.textContent = `${disease}: ${data.probabilities[disease].toFixed(2)}%`;
                } else {
                    listItem.textContent = `${disease}: (Probability not available)`;
                }
                probList.appendChild(listItem);
            }
             resultDiv.innerHTML += '<h2>Probabilities:</h2>';
            resultDiv.appendChild(probList);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = '<p>An error occurred. Please try again.</p>';
    });
}
