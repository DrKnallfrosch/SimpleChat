<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Chat Room</title>
        <link rel="stylesheet" type="text/css" href="../style/style.css"/>
    </head>
    <body>
        <div class="chat-container">
            <h1>Chat Room</h1>
            <div class="chat-box" id="chat-box">
                <!-- Messages will be dynamically inserted here -->
            </div>
            <form id="message-form">
                <input type="text" id="message-input" placeholder="Type your message here..." required>
                <button type="submit">Send</button>
            </form>
        </div>
    </body>

</html>