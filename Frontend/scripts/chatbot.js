// Toggle chatbot visibility when header is clicked
document.getElementById('chatbot-header').onclick = function () {
   const content = document.getElementById('chatbot-content');
   if (content.style.display === 'none' || content.style.display === '') {
      content.style.display = 'block';
   } else {
      content.style.display = 'none';
   }
};

// Function to append messages to chat
function appendMessage(content, sender = 'user') {
   const messageElement = document.createElement('div');
   messageElement.textContent = sender === 'user' ? `Tú: ${content}` : `Sistema: ${content}`;
   document.getElementById('chatbot-messages').appendChild(messageElement);
}

// Send message functionality
document.getElementById('send-button').onclick = async function () {
   const inputField = document.getElementById('chatbot-input');
   const message = inputField.value.trim();

   if (message) {
      // Append the user's message to the chat
      appendMessage(message, 'user');

      // Clear input field
      inputField.value = '';

      // Send the message to the backend
      try {
         const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: {
               'Content-Type': 'application/json',
            },
            body: JSON.stringify({texto: message}),
         });
         
         const data = await response.json();
         
         // Append the bot's response to the chat
         appendMessage(data, 'bot');
      } catch (error) {
         console.error('Error:', error);
         appendMessage('Error: Failed to contact server', 'bot');
      }
   }
};
