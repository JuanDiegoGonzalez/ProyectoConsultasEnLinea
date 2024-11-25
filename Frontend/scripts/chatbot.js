// ---------------------------------
// URL del Backend
// ---------------------------------
const apiBaseUrl = "http://127.0.0.1:8000";

// ---------------------------------
// Mostrar el chatbot y enviar mensaje de bienvenida después de 3 segundos
// ---------------------------------
window.onload = function () {
   setTimeout(function () {
      const content = document.getElementById('chatbot-content');
      content.style.display = 'block'; // Mostrar el contenido del chatbot
   }, 1500); // 1500 ms = 1.5 segundos
   restartVariables()
};

// ---------------------------------
// Alternar la visibilidad del chatbot cuando se hace clic en el encabezado
// ---------------------------------
document.getElementById('chatbot-header').onclick = function () {
   const content = document.getElementById('chatbot-content');
   if (content.style.display === 'none' || content.style.display === '') {
      content.style.display = 'block';
   } else {
      content.style.display = 'none';
   }
};

// ---------------------------------
// Funcion para agregar mensajes al chat
// ---------------------------------
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

   // Agrega el mensaje al chat
   document.getElementById('chatbot-messages').appendChild(messageElement);

   // Scroll automático hacia el final
   const messagesContainer = document.getElementById('chatbot-messages');
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ---------------------------------
// Funcion para agregar el preview al chat
// ---------------------------------
function appendPreview(parsedJson) {
   // Crea la estructura de la tabla
   const table = document.createElement('table');
   table.classList.add('chatbot-table');

   // Crea el encabezado de la tabla
   const headerRow = document.createElement('tr');
   for (const key in parsedJson) {
      if (parsedJson.hasOwnProperty(key)) {
         const headerCell = document.createElement('th');
         headerCell.textContent = key;
         headerRow.appendChild(headerCell);
      }
   }
   table.appendChild(headerRow);

   // Crea las filas de la tabla
   const row = document.createElement('tr');
   for (const key in parsedJson) {
      if (parsedJson.hasOwnProperty(key)) {
         const dataCell = document.createElement('td');
         dataCell.textContent = parsedJson[key];
         row.appendChild(dataCell);
      }
   }
   table.appendChild(row);

   // Agrega la tabla al mensaje
   const tableMessage = document.createElement('div');
   tableMessage.classList.add('message', 'bot');
   tableMessage.appendChild(table);
   
   // Agrega el preview al chat
   document.getElementById('chatbot-messages').appendChild(tableMessage);

   // Scroll automático hacia el final
   const messagesContainer = document.getElementById('chatbot-messages');
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ---------------------------------
// Funcion para agregar el link de descarga al chat
// ---------------------------------
function appendDownloadLink(url) {
   const downloadLink = document.createElement('a');
   downloadLink.href = '#';
   downloadLink.textContent = 'Descargar PDF';
   downloadLink.style.color = '#007bff';
   downloadLink.style.textDecoration = 'underline';

   // Agrega un event listener para descargar el PDF
   downloadLink.addEventListener('click', async (event) => {
       event.preventDefault();
       const filename = url;
       
       try {
           // Hace la petición del pdf al Backend
           const response = await fetch(`${apiBaseUrl}/reports/${filename}`);
           if (response.ok) {
               const blob = await response.blob();
               const url = URL.createObjectURL(blob);
               
               // Crea un link temporal para iniciar la descarga
               const tempLink = document.createElement('a');
               tempLink.href = url;
               tempLink.download = filename;
               tempLink.click();
               URL.revokeObjectURL(url);
           } else {
               console.error('No se pudo descargar el archivo:', response.statusText);
           }
       } catch (error) {
           console.error('Error al descargar el PDF:', error);
       }
   });

   // Agrega el link al chat
   document.getElementById('chatbot-messages').appendChild(downloadLink);

   // Scroll automático hacia el final
   const messagesContainer = document.getElementById('chatbot-messages');
   messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ---------------------------------
// Envio del mensaje y manejo de la respuesta
// ---------------------------------
document.getElementById('send-button').onclick = async function () {
   const inputField = document.getElementById('chatbot-input');
   const message = inputField.value.trim();

   if (message) {
      appendMessage(message, 'user');
      inputField.value = '';

      // Envía el mensaje al Backend
      try {
         const response = await fetch(`${apiBaseUrl}/talk`, {
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

            // Agrega el preview
            const parsedJson = JSON.parse(data.text);
            appendPreview(parsedJson);

            // Notifica al usuario con la opcion para descargar el PDF
            appendMessage('Haz click para descargar el reporte como PDF.', 'bot');
            
            // Agrega el link de descarga
            appendDownloadLink(data.pdf_url, 'bot');
         }
         // Si no, es un mensaje normal, solamente lo agrega
         else {
            appendMessage(data, 'bot');
         }
      } catch (error) {
         console.error('Error:', error);
         appendMessage('Error: No se pudo contactar al servidor', 'bot');
      }
   }
};

// ---------------------------------
// Nueva consulta
// ---------------------------------
async function restartVariables() {
   try {
      const response = await fetch(`${apiBaseUrl}/new`, {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
         }
      });
      appendMessage('Hola! ¿En qué puedo ayudarte hoy?', 'bot');
   } catch (error) {
      console.error('Error:', error);
      appendMessage('Error: No se pudo contactar al servidor', 'bot');
   }
}

document.getElementById('new-button').onclick = async function () {
   restartVariables()
};
