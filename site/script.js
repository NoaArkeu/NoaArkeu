const glow = document.getElementById("cursorGlow");
window.addEventListener("pointermove", (e) => {
  glow.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%, -50%)`;
});

const clockEl = document.getElementById("clock");
const dateTextEl = document.getElementById("dateText");
function updateClock() {
  const n = new Date();
  clockEl.textContent = [n.getHours(), n.getMinutes(), n.getSeconds()].map(v => String(v).padStart(2, "0")).join(":");
  dateTextEl.textContent = `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, "0")}-${String(n.getDate()).padStart(2, "0")}`;
}
updateClock();
setInterval(updateClock, 1000);

const greetTitle = document.getElementById("greetTitle");
const greetDesc = document.getElementById("greetDesc");
(() => {
  const h = new Date().getHours();
  greetTitle.textContent = h < 6 ? "Good night 🌙" : h < 12 ? "Good morning ☀️" : h < 18 ? "Good afternoon 🌤" : "Good evening 🌆";
  greetDesc.textContent = "I'm Noa, nice to meet you!";
})();

const waveBtn = document.getElementById("waveBtn");
const waveText = document.getElementById("waveText");
waveBtn.addEventListener("click", () => {
  const arr = ["Welcome! 👋", "Glad you're here ✨", "Have a great day 🌸", "Let's keep building 🚀"];
  waveText.textContent = arr[Math.floor(Math.random() * arr.length)];
});

const calTitle = document.getElementById("calTitle");
const calGrid = document.getElementById("calendarGrid");
let vy = (new Date()).getFullYear();
let vm = (new Date()).getMonth();
function renderCal(y, m) {
  calGrid.innerHTML = "";
  calTitle.textContent = `${y} / ${String(m + 1).padStart(2, "0")}`;
  let first = new Date(y, m, 1).getDay();
  first = first === 0 ? 7 : first;
  const days = new Date(y, m + 1, 0).getDate();
  for (let i = 1; i < first; i++) {
    const s = document.createElement("span");
    s.className = "mute";
    calGrid.appendChild(s);
  }
  const t = new Date();
  for (let d = 1; d <= days; d++) {
    const s = document.createElement("span");
    s.textContent = d;
    if (y === t.getFullYear() && m === t.getMonth() && d === t.getDate()) s.classList.add("today");
    calGrid.appendChild(s);
  }
}
renderCal(vy, vm);
document.getElementById("prevMonth").onclick = () => { vm--; if (vm < 0) { vm = 11; vy--; } renderCal(vy, vm); };
document.getElementById("nextMonth").onclick = () => { vm++; if (vm > 11) { vm = 0; vy++; } renderCal(vy, vm); };

(async function loadRepos() {
  const el = document.getElementById("projectList");
  try {
    const r = await fetch("https://api.github.com/users/NoaArkeu/repos?sort=pushed&per_page=10");
    const repos = await r.json();
    const top = repos.filter(x => !x.fork).filter(x => (x.name || "").toLowerCase() !== "noaarkeu").slice(0, 3);
    el.innerHTML = top.length
      ? top.map(x => `<a class="repo-item" href="${x.html_url}" target="_blank" rel="noreferrer"><div class="name">${x.name}</div><div class="meta">${x.language || "Unknown"} · ★ ${x.stargazers_count || 0}</div></a>`).join("")
      : `<p class="loading">No public projects yet.</p>`;
  } catch {
    el.innerHTML = "<p class='loading'>Failed to load projects.</p>";
  }
})();

(async function loadWeather() {
  const tempEl = document.getElementById("weatherTemp");
  const cityEl = document.getElementById("weatherCity");
  const descEl = document.getElementById("weatherDesc");
  const emoEl = document.getElementById("weatherEmoji");
  const updEl = document.getElementById("weatherUpdate");
  try {
    const city = "Shanghai";
    const geo = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`).then(r => r.json());
    const g = geo.results?.[0];
    if (!g) throw new Error();
    cityEl.textContent = `${g.name}, ${g.country}`;
    const w = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${g.latitude}&longitude=${g.longitude}&current=temperature_2m,weather_code&timezone=Asia%2FShanghai`).then(r => r.json());
    const c = w.current || {};
    tempEl.textContent = `${c.temperature_2m ?? "--"}°C`;
    const code = c.weather_code;
    const map = (k) => k === 0 ? ["☀️", "Clear sky, perfect for coding."]
      : [1, 2].includes(k) ? ["🌤️", "Soft clouds, calm focus mode."]
      : k === 3 ? ["☁️", "Cloudy vibes, cozy productivity."]
      : [61, 63, 65, 80, 81, 82].includes(k) ? ["🌧️", "Rainy day, stay in and build."]
      : ["🌈", "A lovely day to create."];
    const [emo, txt] = map(code);
    emoEl.textContent = emo;
    descEl.textContent = txt;
    updEl.textContent = `Updated: ${new Date().toLocaleString("en-US")}`;
  } catch {
    descEl.textContent = "Failed to fetch weather. Try again later.";
  }
})();

const openIot = document.getElementById("openIot");
const iotPanel = document.getElementById("iotPanel");
const backHome = document.getElementById("backHome");
const board = document.getElementById("mainBoard");
openIot?.addEventListener("click", (e) => { e.preventDefault(); board.classList.add("hidden"); iotPanel.classList.remove("hidden"); });
backHome?.addEventListener("click", () => { iotPanel.classList.add("hidden"); board.classList.remove("hidden"); });

const audio = document.getElementById("audio");
const playBtn = document.getElementById("playBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const musicBar = document.getElementById("musicBar");
const musicStatus = document.getElementById("musicStatus");
const timeText = document.getElementById("timeText");
const musicCard = document.getElementById("music");

function fmt(sec) {
  if (!Number.isFinite(sec)) return "00:00";
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

playBtn?.addEventListener("click", async () => {
  try {
    if (audio.paused) {
      await audio.play();
      playBtn.textContent = "⏸";
      musicStatus.textContent = "Now playing...";
      musicCard.classList.add("playing");
    } else {
      audio.pause();
      playBtn.textContent = "▶";
      musicStatus.textContent = "Paused";
      musicCard.classList.remove("playing");
    }
  } catch {
    musicStatus.textContent = "Playback failed. Check ./assets/music/clair_de_lune.ogg";
    musicCard.classList.remove("playing");
  }
});

prevBtn?.addEventListener("click", () => { audio.currentTime = 0; });
nextBtn?.addEventListener("click", () => { audio.currentTime = 0; });

audio?.addEventListener("timeupdate", () => {
  const p = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
  musicBar.style.width = `${p}%`;
  timeText.textContent = `${fmt(audio.currentTime)} / ${fmt(audio.duration)}`;
});
audio?.addEventListener("ended", () => {
  playBtn.textContent = "▶";
  musicStatus.textContent = "Playback ended";
  musicCard.classList.remove("playing");
  musicBar.style.width = "0%";
});
audio?.addEventListener("pause", () => musicCard.classList.remove("playing"));
audio?.addEventListener("play", () => musicCard.classList.add("playing"));