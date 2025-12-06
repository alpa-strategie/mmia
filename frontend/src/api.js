/**
 * Client API pour le backend MMiA (Mes Mentors IA).
 */

const API_BASE = 'http://localhost:8001';

export const api = {
  /**
   * Liste toutes les conversations.
   */
  async listConversations() {
    const response = await fetch(`${API_BASE}/api/conversations`);
    if (!response.ok) {
      throw new Error('Échec de la liste des conversations');
    }
    return response.json();
  },

  /**
   * Crée une nouvelle conversation.
   */
  async createConversation() {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error('Échec de la création de la conversation');
    }
    return response.json();
  },

  /**
   * Obtient une conversation spécifique.
   */
  async getConversation(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`
    );
    if (!response.ok) {
      throw new Error('Échec de l\'obtention de la conversation');
    }
    return response.json();
  },

  /**
   * Envoie un message dans une conversation.
   */
  async sendMessage(conversationId, content) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error('Échec de l\'envoi du message');
    }
    return response.json();
  },

  /**
   * Envoie un message et reçoit des mises à jour en streaming.
   * @param {string} conversationId - L'ID de la conversation
   * @param {string} content - Le contenu du message
   * @param {function} onEvent - Fonction de rappel pour chaque événement: (eventType, data) => void
   * @returns {Promise<void>}
   */
  async sendMessageStream(conversationId, content, onEvent) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error('Échec de l\'envoi du message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data);
            onEvent(event.type, event);
          } catch (e) {
            console.error('Échec de l\'analyse de l\'événement SSE:', e);
          }
        }
      }
    }
  },
};
