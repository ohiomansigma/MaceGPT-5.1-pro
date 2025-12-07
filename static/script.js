async function askMonke(event) {
    event.preventDefault();
    const question = document.querySelector("input[name='question']").value;
    const answerBox = document.getElementById('answerBox');
    
    if (!question.trim()) {
        answerBox.textContent = "Please enter a question!";
        return;
    }
    
    answerBox.textContent = "Thinking...";
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        answerBox.textContent = data.answer || data.error || "Something went wrong";
    } catch (error) {
        answerBox.textContent = "Error: " + error.message;
    }
}
