class ChatApp {
    constructor() {
        this.lastMessageId = 0;
        this.sessionCheckInterval = null;
        this.messagePollInterval = null;
        this.isScrolledToBottom = true;
        this.init();
    }

    init() {
        this.messageContainer = document.getElementById('messageContainer');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');

        this.startSessionMonitoring();
        this.loadMessages();
        this.setupEventListeners();
        this.startMessagePolling();
    }

    setupEventListeners() {
        this.messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.messageContainer.addEventListener('scroll', () => {
            const { scrollTop, scrollHeight, clientHeight } = this.messageContainer;
            this.isScrolledToBottom = (scrollHeight - scrollTop - clientHeight) < 50;
        });
    }

    async startSessionMonitoring() {
        // Überprüfe Session alle 30 Sekunden
        this.sessionCheckInterval = setInterval(async () => {
            await this.checkSession();
        }, 30000);

        // Initiale Überprüfung
        await this.checkSession();
    }

    async checkSession() {
        try {
            const response = await fetch('/check_session');
            const data = await response.json();

            if (!data.valid) {
                this.handleSessionExpired();
                return;
            }

            // Zeige Warnung wenn Session bald abläuft
            if (data.remaining_time < 60) {
                this.showSessionWarning(data.remaining_time);
            }

        } catch (error) {
            console.error('Error checking session:', error);
        }
    }

    handleSessionExpired() {
        // Stoppe alle Intervalle
        clearInterval(this.sessionCheckInterval);
        clearInterval(this.messagePollInterval);

        // Zeige Nachricht an
        this.showSessionExpiredMessage();

        // Deaktiviere Formular
        this.messageInput.disabled = true;
        this.messageForm.querySelector('button').disabled = true;

        // Redirect nach 3 Sekunden
        setTimeout(() => {
            window.location.href = '/login?error=Session expired';
        }, 3000);
    }

    showSessionExpiredMessage() {
        const existingWarning = document.querySelector('.session-expired-warning');
        if (existingWarning) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'session-expired-warning';
        messageDiv.innerHTML = `
            <div style="background: #f8d7da; color: #721c24; padding: 15px; 
                       border: 1px solid #f5c6cb; border-radius: 5px;">
                <strong>Session abgelaufen!</strong> 
                Sie werden in 3 Sekunden zum Login weitergeleitet...
            </div>
        `;

        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showSessionWarning(remainingTime) {
        const existingWarning = document.querySelector('.session-warning');
        if (existingWarning) {
            existingWarning.remove();
        }

        const warningDiv = document.createElement('div');
        warningDiv.className = 'session-warning';
        warningDiv.innerHTML = `
            <div style="background: #fff3cd; color: #856404; padding: 10px; 
                       border: 1px solid #ffeaa7; border-radius: 5px;">
                ⚠️ Ihre Session läuft in ${remainingTime} Sekunden ab
            </div>
        `;

        this.messageContainer.appendChild(warningDiv);

        // Entferne Warnung nach 5 Sekunden
        setTimeout(() => {
            warningDiv.remove();
        }, 5000);
    }

    async loadMessages() {
        try {
            const response = await fetch(`/api/messages?last_id=${this.lastMessageId}`);
            const data = await response.json();

            if (data.error) {
                if (data.error === 'Session expired') {
                    this.handleSessionExpired();
                    return;
                }
                console.error('Error loading messages:', data.error);
                return;
            }

            // Entferne Lade-Nachricht
            const loadingMessage = this.messageContainer.querySelector('.loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }

            if (data.messages && data.messages.length > 0) {
                this.displayMessages(data.messages);
                this.lastMessageId = data.messages[data.messages.length - 1].id;

                if (this.isScrolledToBottom) {
                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    displayMessages(messages) {
        messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            this.messageContainer.appendChild(messageElement);
        });
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.username === document.body.getAttribute('data-username') ? 'own' : 'other'}`;

        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${this.escapeHtml(message.username)}</strong>
                <span>${message.timestamp}</span>
            </div>
            <div class="message-text">${this.escapeHtml(message.message)}</div>
        `;

        return messageDiv;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Deaktiviere Input während des Sendens
        this.messageInput.disabled = true;
        const submitButton = this.messageForm.querySelector('button');
        submitButton.disabled = true;
        submitButton.textContent = 'Senden...';

        try {
            const formData = new FormData();
            formData.append('message', message);

            const response = await fetch('/api/send', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.messageInput.value = '';
                this.loadMessages(); // Nachricht sofort anzeigen
            } else if (data.error === 'Session expired') {
                this.handleSessionExpired();
            } else {
                alert('Fehler beim Senden: ' + data.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Fehler beim Senden der Nachricht');
        } finally {
            // Reaktiviere Input
            this.messageInput.disabled = false;
            submitButton.disabled = false;
            submitButton.textContent = 'Senden';
            this.messageInput.focus();
        }
    }

    startMessagePolling() {
        this.messagePollInterval = setInterval(() => {
            this.loadMessages();
        }, 2000);
    }

    scrollToBottom() {
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Chat starten wenn Seite geladen ist
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});