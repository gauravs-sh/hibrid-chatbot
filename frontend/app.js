// --- Configurable API base URL ---
const BASE_API_URL = 'http://localhost:8000/'; // Change to e.g. 'http://localhost:8000' if needed

// --- Token helpers ---
function setToken(token) {
  localStorage.setItem('chatbot_token', token);
}
function getToken() {
  return localStorage.getItem('chatbot_token');
}

// --- Webcam login logic ---
const startWebcamBtn = document.getElementById('startWebcamBtn');
const videoContainer = document.getElementById('videoContainer');
const webcamVideo = document.getElementById('webcamVideo');
const captureBtn = document.getElementById('captureBtn');
const loginMessage = document.getElementById('loginMessage');
let stream = null;

if (startWebcamBtn) {
  startWebcamBtn.onclick = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcamVideo.srcObject = stream;
        videoContainer.style.display = 'block';
        startWebcamBtn.style.display = 'none';
        loginMessage.textContent = '';
      } catch {
        loginMessage.textContent = 'Unable to access webcam.';
      }
    } else {
      loginMessage.textContent = 'Webcam not supported.';
    }
  };
}

if (captureBtn) {
  captureBtn.onclick = async () => {
    if (!webcamVideo.srcObject) return;
    // Capture frame from video
    const canvas = document.createElement('canvas');
    canvas.width = webcamVideo.videoWidth || 320;
    canvas.height = webcamVideo.videoHeight || 240;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const formData = new FormData();
      formData.append('file', blob, 'webcam.jpg');
      loginMessage.textContent = 'Logging in...';
      try {
        const res = await fetch(BASE_API_URL + 'api/login/webcam', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (res.ok && data.token) {
          setToken(data.token);
          loginMessage.textContent = 'Login successful!';
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }
          setTimeout(() => { window.location.href = 'chat.html'; }, 800);
        } else {
          loginMessage.textContent = data.detail || 'Face not detected.';
        }
      } catch {
        loginMessage.textContent = 'Network error.';
      }
    }, 'image/jpeg');
  };
}

// --- Chat page logic ---
const chatForm = document.getElementById('chatForm');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');
const chatResponse = document.getElementById('chatResponse');

function renderMessage(msg, isError = false) {
  if (chatResponse) {
    chatResponse.textContent = msg;
    chatResponse.style.color = isError ? '#c00' : '#444';
  }
}

if (chatForm) {
  // Redirect to login if no token
  if (!getToken()) {
    window.location.href = 'login.html';
  }

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;
    renderMessage('Waiting for response...');
    queryInput.disabled = true;
    sendBtn.disabled = true;
    try {
      const res = await fetch(BASE_API_URL + 'api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'token': getToken() || ''
        },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (res.ok && data.answer) {
        renderMessage(data.answer);
      } else {
        renderMessage(data.detail || 'Error.', true);
      }
    } catch {
      renderMessage('Network error.', true);
    }
    queryInput.disabled = false;
    sendBtn.disabled = false;
    queryInput.value = '';
    queryInput.focus();
  });
}
