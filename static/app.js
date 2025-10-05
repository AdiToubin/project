// Calculator Form Handler
document.getElementById('calculatorForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const num1 = document.getElementById('num1').value;
    const num2 = document.getElementById('num2').value;
    const operation = document.getElementById('operation').value;

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ num1, num2, operation })
        });

        const data = await response.json();
        const resultDiv = document.getElementById('result');

        if (data.success) {
            resultDiv.className = 'success';
            resultDiv.innerHTML = `<strong>Result:</strong> ${data.result}`;
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${data.message || 'Calculation failed'}`;
        }
    } catch (error) {
        document.getElementById('result').className = 'error';
        document.getElementById('result').innerHTML = `<strong>Error:</strong> ${error.message}`;
    }
});

// Data Processor Form Handler
document.getElementById('dataForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const dataInput = document.getElementById('dataInput').value;

    try {
        const jsonData = JSON.parse(dataInput || '{}');

        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        });

        const data = await response.json();
        const resultDiv = document.getElementById('processResult');

        if (data.status === 'success') {
            resultDiv.className = 'success';
            resultDiv.innerHTML = `<strong>${data.message}</strong><pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `<strong>Error:</strong> ${data.message}`;
        }
    } catch (error) {
        document.getElementById('processResult').className = 'error';
        document.getElementById('processResult').innerHTML = `<strong>Error:</strong> ${error.message}`;
    }
});
