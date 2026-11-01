const overlay = document.getElementById('chatOverlay');
const messages = document.getElementById('messages');
let activeCharacter = 'Meera';
const chatHistory = { Meera: [], Aanya: [] };

const GALLERY_DB = 'meera-private-gallery';
const GALLERY_STORE = 'images';
function openGalleryDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(GALLERY_DB, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(GALLERY_STORE, { keyPath: 'id' });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
async function saveGalleryImage(item) {
  const db = await openGalleryDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(GALLERY_STORE, 'readwrite');
    tx.objectStore(GALLERY_STORE).put(item);
    tx.oncomplete = () => { db.close(); resolve(); };
    tx.onerror = () => { db.close(); reject(tx.error); };
  });
}
async function getGalleryImages() {
  const db = await openGalleryDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(GALLERY_STORE, 'readonly');
    const req = tx.objectStore(GALLERY_STORE).getAll();
    req.onsuccess = () => { db.close(); resolve((req.result || []).sort((a,b) => b.createdAt-a.createdAt)); };
    req.onerror = () => { db.close(); reject(req.error); };
  });
}
async function deleteGalleryImage(id) {
  const db = await openGalleryDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(GALLERY_STORE, 'readwrite');
    tx.objectStore(GALLERY_STORE).delete(id);
    tx.oncomplete = () => { db.close(); resolve(); };
    tx.onerror = () => { db.close(); reject(tx.error); };
  });
}
const galleryOverlay = document.createElement('div');
galleryOverlay.className = 'gallery-overlay';
galleryOverlay.innerHTML = '<section class="gallery-panel"><header><div><strong>My Gallery</strong><small>Private on this device</small></div><button type="button" aria-label="Close gallery">✕</button></header><div class="gallery-grid"></div></section>';
document.body.appendChild(galleryOverlay);
galleryOverlay.querySelector('header button').addEventListener('click', () => galleryOverlay.classList.remove('open'));
galleryOverlay.addEventListener('click', e => { if (e.target === galleryOverlay) galleryOverlay.classList.remove('open'); });
async function openGallery() {
  galleryOverlay.classList.add('open');
  const grid = galleryOverlay.querySelector('.gallery-grid');
  grid.textContent = 'Loading your saved selfies…';
  try {
    const items = await getGalleryImages();
    grid.replaceChildren();
    if (!items.length) { grid.textContent = 'Your gallery is empty. Generate a selfie with the ＋ button in chat.'; return; }
    items.forEach(item => {
      const card = document.createElement('article');
      card.className = 'gallery-card';
      const image = document.createElement('img');
      image.src = item.image; image.alt = item.character + ' saved selfie';
      image.addEventListener('click', () => openImageViewer(item.image, image.alt));
      const meta = document.createElement('div');
      meta.className = 'gallery-meta';
      const label = document.createElement('span');
      label.textContent = item.character + ' · ' + new Date(item.createdAt).toLocaleDateString();
      const remove = document.createElement('button');
      remove.type = 'button'; remove.textContent = 'Delete';
      remove.addEventListener('click', async () => { await deleteGalleryImage(item.id); card.remove(); if (!grid.children.length) grid.textContent = 'Your gallery is empty.'; });
      meta.append(label, remove); card.append(image, meta); grid.append(card);
    });
  } catch (_) { grid.textContent = 'Gallery storage is unavailable in this browser.'; }
}


function storageKey(name) { return 'meera-chat-' + name.toLowerCase(); }
function memoryKey(name) { return 'meera-memory-' + name.toLowerCase(); }
function loadMemory(name) {
  try {
    const saved = JSON.parse(localStorage.getItem(memoryKey(name)) || '[]');
    return Array.isArray(saved) ? saved.filter(x => typeof x === 'string').slice(-30) : [];
  } catch (_) { return []; }
}
function saveMemoryFact(name, message) {
  const text = message.trim();
  if (!/(\\bremember\\b|\\bmy name is\\b|\\bcall me\\b|\\bi like\\b|\\bi love\\b|\\bi prefer\\b|\\bi work\\b|\\bi study\\b|\\bmy favourite\\b|\\bmy favorite\\b|\\bi live in\\b)/i.test(text)) return;
  const facts = loadMemory(name);
  if (!facts.some(x => x.toLowerCase() === text.toLowerCase())) {
    facts.push(text.slice(0, 300));
    try { localStorage.setItem(memoryKey(name), JSON.stringify(facts.slice(-30))); } catch (_) {}
  }
}
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
const imageViewer = document.createElement('div');
imageViewer.className = 'image-viewer';
imageViewer.setAttribute('aria-hidden', 'true');
imageViewer.innerHTML = `
  <div class="image-viewer-toolbar">
    <button class="viewer-action viewer-download" type="button" aria-label="Download image" title="Download">⬇️</button>
    <button class="viewer-action viewer-close" type="button" aria-label="Close image" title="Close">✕</button>
  </div>
  <img class="image-viewer-image" alt="Full-size AI portrait">
`;
document.body.appendChild(imageViewer);
const viewerImage = imageViewer.querySelector('.image-viewer-image');
imageViewer.querySelector('.viewer-close').addEventListener('click', closeImageViewer);
imageViewer.addEventListener('click', event => { if (event.target === imageViewer) closeImageViewer(); });
imageViewer.querySelector('.viewer-download').addEventListener('click', () => {
  if (!viewerImage.src) return;
  const link = document.createElement('a');
  link.href = viewerImage.src;
  link.download = (activeCharacter || 'meera').toLowerCase() + '-selfie-' + Date.now() + '.png';
  document.body.appendChild(link);
  link.click();
  link.remove();
});
function openImageViewer(src, alt) {
  viewerImage.src = src;
  viewerImage.alt = alt || 'Full-size AI portrait';
  imageViewer.classList.add('open');
  imageViewer.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}
function closeImageViewer() {
  imageViewer.classList.remove('open');
  imageViewer.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
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
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeImageViewer(); closeChat(); galleryOverlay.classList.remove('open'); } });
document.querySelectorAll('.heart').forEach(btn => btn.addEventListener('click', e => {
  e.stopPropagation();
  btn.classList.toggle('liked');
  btn.textContent = btn.classList.contains('liked') ? '♥' : '♡';
}));
document.getElementById('startChat').addEventListener('click', () => openChat());
document.querySelector('.composer-plus').addEventListener('click', async () => {
  const button = document.querySelector('.composer-plus');
  button.disabled = true;
  const pending = addMessage(activeCharacter + ' is taking a selfie…', 'received');
  try {
    const response = await fetch('/api/selfie', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character: activeCharacter })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(errorMessage(data.detail, 'Image generation failed.'));
    pending.replaceChildren();
    const image = document.createElement('img');
    image.src = data.image;
    image.alt = activeCharacter + ' portrait';
    image.style.cssText = 'display:block;width:min(100%,420px);height:auto;max-height:70vh;object-fit:contain;border-radius:16px;cursor:zoom-in;';
    image.addEventListener('click', () => openImageViewer(image.src, image.alt));
    pending.appendChild(image);
    const caption = document.createElement('small');
    caption.textContent = 'AI-generated portrait';
    pending.appendChild(caption);
    try { await saveGalleryImage({ id: Date.now() + '-' + Math.random().toString(16).slice(2), character: activeCharacter, image: data.image, createdAt: Date.now() }); } catch (_) { /* Chat image remains available even if gallery storage is full. */ }
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
  if (btn.dataset.view === 'gallery') openGallery();
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
  saveMemoryFact(activeCharacter, message);
  input.value = '';
  input.disabled = true;
  const sendButton = document.querySelector('.send-button');
  sendButton.disabled = true;
  const pending = addMessage('Thinking…', 'received');

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, character: activeCharacter, history, memory: loadMemory(activeCharacter) })
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
