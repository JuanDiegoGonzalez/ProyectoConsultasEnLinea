// Mostrar el chatbot y enviar mensaje de bienvenida después de 3 segundos
window.onload = function () {
   setTimeout(function () {
      const content = document.getElementById('chatbot-content');
      content.style.display = 'block'; // Mostrar el contenido del chatbot

      // Mensaje de bienvenida al usuario
      appendMessage('Hola! ¿En qué puedo ayudarte hoy?', 'bot');
   }, 1500); // 1500 ms = 1.5 segundos
};

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

   // Añadir la clase correcta dependiendo del remitente
   messageElement.classList.add('message');
   if (sender === 'user') {
      messageElement.classList.add('user');
   } else {
      messageElement.classList.add('bot');
   }

   document.getElementById('chatbot-messages').appendChild(messageElement);

   // Scroll automático hacia el final cuando se añaden nuevos mensajes
   const messagesContainer = document.getElementById('chatbot-messages');
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
         const response = await fetch('http://127.0.0.1:8000/talk', {
            method: 'POST',
            headers: {
               'Content-Type': 'application/json',
            },
            body: JSON.stringify({texto: message}),
         });
         
         const contentType = response.headers.get('Content-Type');

         if (contentType === 'application/pdf') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'response.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
         }
         else {
            const data = await response.json();
            appendMessage(data, 'bot');
         }
      } catch (error) {
         console.error('Error:', error);
         appendMessage('Error: Failed to contact server', 'bot');
      }
   }
};

// Nueva consulta
document.getElementById('new-button').onclick = async function () {
   try {
      const response = await fetch('http://127.0.0.1:8000/new', {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
         }
      });
      appendMessage('Hola! ¿En qué puedo ayudarte hoy?', 'bot');
   } catch (error) {
      console.error('Error:', error);
      appendMessage('Error: Failed to contact server', 'bot');
   }
};
