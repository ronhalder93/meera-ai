const overlay=document.getElementById('chatOverlay');
const messages=document.getElementById('messages');
let activeCharacter='Meera';
function openChat(name='Meera'){
  activeCharacter=name;
  const initial=name==='Aanya'?'A':'M';
  document.getElementById('chatName').textContent=name;
  document.getElementById('chatAvatar').textContent=initial;
  document.getElementById('chatLargeAvatar').textContent=initial;
  document.getElementById('chatWelcome').textContent='A little hello from '+name;
  messages.innerHTML='<div class="message received">Hey! I\'m glad you\'re here. How\'s your day going?<small>Just now</small></div>';
  overlay.classList.add('open');overlay.setAttribute('aria-hidden','false');
  setTimeout(()=>document.getElementById('messageInput').focus(),100);
}
function closeChat(){overlay.classList.remove('open');overlay.setAttribute('aria-hidden','true')}
document.querySelectorAll('[data-open]').forEach(card=>card.addEventListener('click',()=>openChat(card.dataset.open)));
document.querySelectorAll('.companion-link').forEach(link=>link.addEventListener('click',()=>{document.querySelectorAll('.companion-link').forEach(x=>x.classList.remove('selected'));link.classList.add('selected');openChat(link.dataset.character)}));
document.getElementById('closeChat').addEventListener('click',closeChat);
overlay.addEventListener('click',e=>{if(e.target===overlay)closeChat()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeChat()});
document.querySelectorAll('.heart').forEach(btn=>btn.addEventListener('click',e=>{e.stopPropagation();btn.classList.toggle('liked');btn.textContent=btn.classList.contains('liked')?'♥':'♡'}));
document.getElementById('startChat').addEventListener('click',()=>openChat());
document.getElementById('exploreBtn').addEventListener('click',()=>document.getElementById('characterGrid').scrollIntoView({behavior:'smooth'}));
document.getElementById('allCharacters').addEventListener('click',()=>document.getElementById('characterGrid').scrollIntoView({behavior:'smooth'}));
document.getElementById('createCharacter').addEventListener('click',()=>alert('Character creation is coming in the next build.'));
document.querySelectorAll('.nav-item').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));btn.classList.add('active');document.getElementById('crumb').textContent=btn.textContent.trim();if(btn.dataset.view==='gallery')alert('Your private gallery is coming in the next build.');if(btn.dataset.view==='chats')openChat()}));
document.getElementById('chatForm').addEventListener('submit',async e=>{
  e.preventDefault();const input=document.getElementById('messageInput');const text=input.value.trim();if(!text)return;
  const sent=document.createElement('div');sent.className='message sent';sent.textContent=text;messages.appendChild(sent);input.value='';messages.scrollTop=messages.scrollHeight;
  const pending=document.createElement('div');pending.className='message received';pending.textContent='Thinking…';messages.appendChild(pending);messages.scrollTop=messages.scrollHeight;
  try{const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,character:activeCharacter})});const data=await response.json();pending.textContent=data.reply;const note=document.createElement('small');note.textContent='Demo reply';pending.appendChild(note)}
  catch(error){pending.textContent='I’m here with you. The demo server could not be reached just now.'}
  messages.scrollTop=messages.scrollHeight;
});
