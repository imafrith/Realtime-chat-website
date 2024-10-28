document.addEventListener('DOMContentLoaded', function () {
    const protocol = window.location.protocol === 'http:' ? 'ws://' : 'ws://';
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    const path = '/ws/chats/';  // Adjust the path as needed

    const socket = new WebSocket(`${protocol}${hostname}${port}${path}`);

    socket.onopen = function(event) {
        console.log('WebSocket connection established.');
        // You might want to request the latest chats immediately
        socket.send(JSON.stringify({ 'command': 'fetch_latest_chats' }));
    };

    socket.onclose = function(event) {
        console.log('WebSocket connection closed.');
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Message received from server:', data);

        // Ensure data.latest_chat is an array
        if (Array.isArray(data.latest_chat)) {
            updateChatList(data.latest_chat);
        } else {
            console.error('Invalid data received from server.');
        }
    };

    function updateChatList(latestChatData) {
        const chatList = document.getElementById('chat-list');
        chatList.innerHTML = ''; // Clear existing chat list
    
        latestChatData.forEach(chat => {
            const item = document.createElement('li');
            item.innerHTML = `
                <a href="/chat/room/${chat.message.group_name}">
                    <div class="d-flex">
                        <div class="chat-user-img online align-self-center me-3 ms-0">
                            <img src="${chat.profile_photo}" class="rounded-circle avatar-xs" alt="">
                            <span class="user-status"></span>
                        </div>
                        <div class="flex-grow-1 overflow-hidden">
                            <h5 class="text-truncate font-size-15 mb-1">
                                ${chat.receiver}
                            </h5>
                            <p class="chat-user-message text-truncate mb-0">
                                ${chat.message.content|| 'No messages yet'}
                            </p>
                        </div>
                        <div class="font-size-11">
                            ${new Date(chat.message.created).toLocaleTimeString()}
                        </div>
                        <div class="unread-message">
                            ${chat.new_message_count > 0 ?
                                (chat.new_message_count > 5 ?
                                    `<span class="badge badge-soft-success rounded-pill">+${chat.new_message_count}</span>` :
                                    `<span class="badge badge-soft-success rounded-pill">${chat.new_message_count}</span>`) :
                                ''}
                        </div>
                    </div>
                </a>
              
            `;
            chatList.appendChild(item);
        });
    }
})