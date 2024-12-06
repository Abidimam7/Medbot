// Start a new chat session
function startNewChat() {
    fetch('/start-new-chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('chatOutput').innerHTML = ''; // Clear the chat output
            loadChatHistories(); // Refresh chat histories in the sidebar
        }
    })
    .catch(error => console.error('Error:', error));
}

// Send a message to the server
function sendMessage() {
    const userMessage = document.getElementById('userInput').value.trim();
    if (!userMessage) {
        alert('Please enter a message');
        return;
    }

    // Display the user's message in the chat
    const chatOutput = document.getElementById('chatOutput');
    chatOutput.innerHTML += `<div class="message user-message"><strong></strong> ${userMessage}</div>`;
    document.getElementById('userInput').value = ''; // Clear input field
    chatOutput.scrollTop = chatOutput.scrollHeight; // Scroll to the latest message

    generateTextResponse(userMessage);
}

// Generate a text-based response (for chatbot conversation)
function generateTextResponse(userMessage) {
    fetch('/response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ message: userMessage }),
    })
    .then(response => response.json())
    .then(data => {
        const botResponse = data.response || 'Sorry, I didn\'t understand that.';
        typeBotResponse(botResponse);
    })
    .catch(error => console.error('Error:', error));
}

function typeBotResponse(response) {
    const chatOutput = document.getElementById('chatOutput');
    const botMessageElement = document.createElement('div');
    botMessageElement.classList.add('message', 'bot-response');
    
    botMessageElement.innerHTML = `
    <div class="bot-logo">
        <img src="${botLogoURL}" alt="Bot Logo" class="bot-logo-img">
    </div>
    <div class="bot-text"></div>
    `;

    chatOutput.appendChild(botMessageElement);

    const botTextElement = botMessageElement.querySelector('.bot-text');
    let index = 0;
    const typingInterval = setInterval(() => {
        botTextElement.innerHTML += response.charAt(index++);
        chatOutput.scrollTop = chatOutput.scrollHeight;
        if (index >= response.length) clearInterval(typingInterval);
    }, 20);
}



// Function to fetch and display chat histories
function loadChatHistories() {
    fetch('/chat-histories/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(response => response.json())
        .then(data => {
            const chatHistoryList = document.getElementById('chatHistoryList');
            chatHistoryList.innerHTML = ''; // Clear existing chat list

            if (data.histories?.length) {
                // Sort histories by timestamp (most recent first)
                data.histories.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

                data.histories.forEach(history => {
                    // Create a chat item
                    const chatItem = document.createElement('li');
                    chatItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

                    // Add the content to the chat item
                    chatItem.innerHTML = `
                        <span class="chat-title">${history.title || 'New Chat'}</span>
                        <div class="dropdown">
                            <i class="fas fa-ellipsis-h text-muted" data-bs-toggle="dropdown" aria-expanded="false"></i>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><button class="dropdown-item" onclick="renameChat('${history.id}')">Rename</button></li>
                                <li><button class="dropdown-item text-danger" onclick="deleteConversation('${history.id}')">Delete</button></li>
                            </ul>
                        </div>
                    `;

                    // Add click event for loading the conversation
                    chatItem.addEventListener('click', () => getConversation(history.id));

                    // Append the chat item to the list
                    chatHistoryList.appendChild(chatItem);
                });
            } else {
                chatHistoryList.innerHTML = '<li class="list-group-item text-muted">No chat history available</li>';
            }
        })
        .catch(error => console.error('Error fetching chat histories:', error));
}

// Function to rename a chat
function renameChat(chatId) {
    const newName = prompt("Enter a new name for this chat:");
    if (!newName) {
        alert("Chat name cannot be empty.");
        return;
    }

    // Show a loading spinner or feedback
    const chatItem = document.querySelector(`[data-id="${chatId}"] .chat-title`);
    if (chatItem) chatItem.textContent = "Renaming...";

    fetch(`/rename-chat/${chatId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ title: newName }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Chat renamed successfully!");
                loadChatHistories(); // Refresh the chat list
            } else {
                alert(data.error || "Error renaming chat.");
            }
        })
        .catch(error => {
            console.error('Error renaming chat:', error);
            alert("An error occurred while renaming the chat.");
        });
}

// Fetch and display a specific conversation
function getConversation(conversationId) {
    fetch(`/get-conversation/${conversationId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        const chatOutput = document.getElementById('chatOutput');
        chatOutput.innerHTML = ''; // Clear existing chat messages

        if (data.messages?.length) {
            data.messages.forEach(msg => {
                if (msg.type === 'file') {
                    chatOutput.innerHTML += `
                        <div class="message ${msg.role}-message">
                            ${msg.role === 'user' ? '<strong></strong>' : `<div class="bot-logo"><img src="${botLogoURL}" alt="Bot Logo" class="bot-logo-img"></div>`} ${msg.content}
                        </div>
                    `;
                } else {
                    chatOutput.innerHTML += `
                        <div class="message ${msg.role}-message">
                            ${msg.role === 'user' ? '<strong></strong>' : `<div class="bot-logo"><img src="${botLogoURL}" alt="Bot Logo" class="bot-logo-img"></div>`} ${msg.content}
                        </div>
                    `;
                }
            });

            chatOutput.scrollTop = chatOutput.scrollHeight;
        } else {
            chatOutput.innerHTML = `<div class="message bot-response"><div class="bot-logo"><img src="${botLogoURL}" alt="Bot Logo" class="bot-logo-img"></div> No messages in this conversation.</div>`;
        }
    })
    .catch(error => console.error('Error fetching conversation:', error));
}



// Delete a conversation
function deleteConversation(conversationId) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This will permanently delete the conversation!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/delete-conversation/${conversationId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Conversation deleted successfully') {
                    Swal.fire(
                        'Deleted!',
                        'Your conversation has been deleted.',
                        'success'
                    );
                    loadChatHistories();
                } else {
                    Swal.fire(
                        'Error!',
                        'An error occurred while deleting the conversation.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Error deleting conversation:', error);
                Swal.fire(
                    'Error!',
                    'Failed to delete the conversation. Please try again.',
                    'error'
                );
            });
        }
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

// Load chat histories on page load
document.addEventListener('DOMContentLoaded', loadChatHistories);
document.getElementById('userInput').addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

// Handle file upload
document.getElementById('fileInput').addEventListener('change', uploadFile);

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload-file/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        const chatOutput = document.getElementById('chatOutput');

        if (data.success) {
            // Display file upload confirmation and summary in the chat
            chatOutput.innerHTML += `
                <div class="message user-message">
                    <strong></strong> Uploaded file: ${file.name}
                </div>
                <div class="message bot-response">
                    <strong>Bot:</strong> File uploaded: <a href="${data.file_url}" target="_blank">View File</a>
                </div>
                <div class="message bot-response">
                    <strong>Bot:</strong> ${data.summary}
                </div>
            `;

            chatOutput.scrollTop = chatOutput.scrollHeight;
        } else {
            alert(data.error || 'Error uploading file.');
        }
    })
    .catch(error => {
        console.error('Error uploading file:', error);
        alert('Failed to upload file.');
    });
}
// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const chatArea = document.getElementById('chatArea');
            sidebar.classList.toggle('d-none');
            chatArea.classList.toggle('col-md-12');
            chatArea.classList.toggle('col-md-9');
        }


