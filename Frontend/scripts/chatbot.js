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

// Funcion to append the preview to chat
function appendPreview(parsedJson) {
   // Create the table structure
   const table = document.createElement('table');
   table.classList.add('chatbot-table');  // Apply the CSS class

   // Create the table header
   const headerRow = document.createElement('tr');
   for (const key in parsedJson) {
      if (parsedJson.hasOwnProperty(key)) {
         const headerCell = document.createElement('th');
         headerCell.textContent = key;
         headerRow.appendChild(headerCell);
      }
   }
   table.appendChild(headerRow);

   // Create the table rows for each value
   const row = document.createElement('tr');
   for (const key in parsedJson) {
      if (parsedJson.hasOwnProperty(key)) {
         const dataCell = document.createElement('td');
         dataCell.textContent = parsedJson[key];
         row.appendChild(dataCell);
      }
   }
   table.appendChild(row);

   // Append the table to the chatbot message
   const tableMessage = document.createElement('div');
   tableMessage.classList.add('message', 'bot');
   tableMessage.appendChild(table);
   
   // Append the table message to the chatbot
   document.getElementById('chatbot-messages').appendChild(tableMessage);

   // Scroll to the bottom of the chat
   const messagesContainer = document.getElementById('chatbot-messages');
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Send message functionality
document.getElementById('send-button').onclick = async function () {
   const inputField = document.getElementById('chatbot-input');
   const message = inputField.value.trim();

   if (message) {
      appendMessage(message, 'user');
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
         
         const data = await response.json();

         // Si la respuesta trae preview + url del PDF generado
         if (data.text && data.pdf_url) {
            appendMessage('Aquí tienes el resultado de la consulta:', 'bot');

            // Append the text message
            const parsedJson = JSON.parse(data.text);
            appendPreview(parsedJson, 'bot');

            // Notify the user with a message and download option
            appendMessage('Haz click para descargar el reporte como PDF.', 'bot');
            const downloadLink = document.createElement('a');
            downloadLink.href = '#';
            downloadLink.textContent = 'Descargar PDF';
            downloadLink.style.color = '#007bff';
            downloadLink.style.textDecoration = 'underline';
        
            // Add click event listener to fetch and download the PDF
            downloadLink.addEventListener('click', async (event) => {
                event.preventDefault();
                const filename = data.pdf_url;
                
                try {
                    // Fetch the PDF from the backend
                    const response = await fetch(`http://127.0.0.1:8000/reports/${filename}`);
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = URL.createObjectURL(blob);
                        
                        // Create a temporary link to trigger the download
                        const tempLink = document.createElement('a');
                        tempLink.href = url;
                        tempLink.download = filename;
                        tempLink.click();  // Trigger the download
        
                        // Revoke the object URL to free up resources
                        URL.revokeObjectURL(url);
                    } else {
                        console.error('Failed to download the file:', response.statusText);
                    }
                } catch (error) {
                    console.error('Error while downloading PDF:', error);
                }
            });
            document.getElementById('chatbot-messages').appendChild(downloadLink);
         }
         // Si no, es un mensaje normal, solamente lo agrega
         else {
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
