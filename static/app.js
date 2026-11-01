const overlay = document.getElementById('chatOverlay');
const messages = document.getElementById('messages');
let activeCharacter = 'Meera';
const chatHistory = { Meera: [], Aanya: [] };

function storageKey(name) { return 'meera-chat-' + name.toLowerCase(); }
function loadHistory(name) {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey(name)) || '[]');
    chatHistory[name] = Array.isArray(saved)
      ? saved.filter(item => item && typeof item.content === 'string' &&
          !item.content.includes('OPENAI_API_KEY') &&
          !item.content.includes('AI connection hasn’t been switched on yet.')).slice(-30)
      : [];
    saveHistory(name);
  } catch (_) { chatHistory[name] = []; }
}
function errorMessage(detail, fallback) {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(item => item && item.msg ? item.msg : JSON.stringify(item)).join('; ');
  if (detail && typeof detail === 'object') return detail.message || detail.msg || JSON.stringify(detail);
  return fallback;
}
function saveHistory(name) {
  try { localStorage.setItem(storageKey(name), JSON.stringify(chatHistory[name].slice(-30))); }
  catch (_) { /* Local storage may be unavailable or full. */ }
}
function addMessage(text, kind, stamp) {
  const node = document.createElement('div');
  node.className = 'message ' + kind;
  node.textContent = text;
  if (stamp) {
    const small = document.createElement('small');
    small.textContent = stamp;
    node.appendChild(small);
  }
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
  return node;
}
function renderHistory(name) {
  messages.replaceChildren();
  if (!chatHistory[name].length) {
    addMessage('Hey! I\'m glad you\'re here. How\'s your day going?', 'received', 'Just now');
    return;
  }
  chatHistory[name].forEach(item => addMessage(item.content, item.role === 'user' ? 'sent' : 'received'));
}
function openChat(name = 'Meera') {
  activeCharacter = name === 'Aanya' ? 'Aanya' : 'Meera';
  loadHistory(activeCharacter);
  const initial = activeCharacter === 'Aanya' ? 'A' : 'M';
  document.getElementById('chatName').textContent = activeCharacter;
  document.getElementById('chatAvatar').textContent = initial;
  document.getElementById('chatLargeAvatar').textContent = initial;
  document.getElementById('chatWelcome').textContent = 'A little hello from ' + activeCharacter;
  renderHistory(activeCharacter);
  overlay.classList.add('open');
  overlay.setAttribute('aria-hidden', 'false');
  setTimeout(() => document.getElementById('messageInput').focus(), 100);
}
function closeChat() {
  overlay.classList.remove('open');
  overlay.setAttribute('aria-hidden', 'true');
}

document.querySelectorAll('[data-open]').forEach(card => card.addEventListener('click', () => openChat(card.dataset.open)));
document.querySelectorAll('.companion-link').forEach(link => link.addEventListener('click', () => {
  document.querySelectorAll('.companion-link').forEach(x => x.classList.remove('selected'));
  link.classList.add('selected');
  openChat(link.dataset.character);
}));
document.getElementById('closeChat').addEventListener('click', closeChat);
overlay.addEventListener('click', e => { if (e.target === overlay) closeChat(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeChat(); });
document.querySelectorAll('.heart').forEach(btn => btn.addEventListener('click', e => {
  e.stopPropagation();
  btn.classList.toggle('liked');
  btn.textContent = btn.classList.contains('liked') ? '♥' : '♡';
}));
document.getElementById('startChat').addEventListener('click', () => openChat());
document.querySelector('.composer-plus').addEventListener('click', async () => {
  const scene = window.prompt('Describe a non-explicit portrait scene (for example: sunset cafe selfie):');
  if (!scene || !scene.trim()) return;
  const button = document.querySelector('.composer-plus');
  button.disabled = true;
  const pending = addMessage('Creating your portrait…', 'received');
  try {
    const response = await fetch('/api/selfie', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character: activeCharacter, scene: scene.trim() })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(errorMessage(data.detail, 'Image generation failed.'));
    pending.replaceChildren();
    const image = document.createElement('img');
    image.src = data.image;
    image.alt = activeCharacter + ' portrait';
    image.style.cssText = 'display:block;max-width:100%;width:280px;border-radius:14px;';
    pending.appendChild(image);
    const caption = document.createElement('small');
    caption.textContent = 'AI-generated portrait';
    pending.appendChild(caption);
  } catch (error) {
    pending.textContent = error.message || 'Image generation is not available yet.';
  } finally {
    button.disabled = false;
    messages.scrollTop = messages.scrollHeight;
  }
});
document.getElementById('exploreBtn').addEventListener('click', () => document.getElementById('characterGrid').scrollIntoView({ behavior: 'smooth' }));
document.getElementById('allCharacters').addEventListener('click', () => document.getElementById('characterGrid').scrollIntoView({ behavior: 'smooth' }));
document.getElementById('createCharacter').addEventListener('click', () => alert('Custom companion creation is coming soon.'));
document.querySelectorAll('.nav-item').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('crumb').textContent = btn.textContent.trim();
  if (btn.dataset.view === 'gallery') alert('The private image gallery is not enabled yet.');
  if (btn.dataset.view === 'chats') openChat();
}));

document.getElementById('chatForm').addEventListener('submit', async e => {
  e.preventDefault();
  const input = document.getElementById('messageInput');
  const message = input.value.trim();
  if (!message) return;

  const history = chatHistory[activeCharacter].slice(-20);
  addMessage(message, 'sent');
  chatHistory[activeCharacter].push({ role: 'user', content: message });
  saveHistory(activeCharacter);
  input.value = '';
  input.disabled = true;
  const sendButton = document.querySelector('.send-button');
  sendButton.disabled = true;
  const pending = addMessage('Thinking…', 'received');

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, character: activeCharacter, history })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(errorMessage(data.detail, 'MEERA could not reply right now.'));
    pending.textContent = data.reply || 'I’m here. Tell me a little more.';
    chatHistory[activeCharacter].push({ role: 'assistant', content: pending.textContent });
    saveHistory(activeCharacter);
  } catch (error) {
    pending.textContent = error.message || 'The server could not be reached. Please try again.';
    // Remove the unanswered user turn so it is not sent as completed conversation context.
    chatHistory[activeCharacter].pop();
    saveHistory(activeCharacter);
  } finally {
    input.disabled = false;
    sendButton.disabled = false;
    input.focus();
    messages.scrollTop = messages.scrollHeight;
  }
});
