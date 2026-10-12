const $ = (selector) => document.querySelector(selector);
const linkTab = $("#link-tab"), fileTab = $("#file-tab"), manualTab = $("#manual-tab"), linkForm = $("#link-form"), fileForm = $("#file-form"), manualForm = $("#manual-form");

function selectMode(mode) {
  const isLink = mode === "link", isFile = mode === "file";
  linkTab.classList.toggle("active", isLink); fileTab.classList.toggle("active", isFile); manualTab.classList.toggle("active", !isLink && !isFile);
  linkTab.setAttribute("aria-selected", isLink); fileTab.setAttribute("aria-selected", isFile); manualTab.setAttribute("aria-selected", !isLink && !isFile);
  linkForm.classList.toggle("hidden", !isLink); fileForm.classList.toggle("hidden", !isFile); manualForm.classList.toggle("hidden", isLink || isFile);
  $("#error").classList.add("hidden");
}
linkTab.onclick = () => selectMode("link"); fileTab.onclick = () => selectMode("file"); manualTab.onclick = () => selectMode("manual");

function setLoading(show) { $("#loading").classList.toggle("hidden", !show); document.querySelectorAll("button").forEach(b => b.disabled = show); }
function displayError(message) { const box=$("#error"); box.textContent=message; box.classList.remove("hidden"); }
function esc(value="") { const el=document.createElement("span"); el.textContent=value; return el.innerHTML; }
const labels = {pay:"Pay & stipend",role_specificity:"Role clarity",reputation:"Company context",location_fit:"Location fit",conversion:"Conversion path",red_flag_absence:"Fair-work signals"};
function displayResults(data) {
  const posting=data.posting || {}; const items=Object.entries(data.breakdown).map(([key,value]) => `<article class="signal"><div class="signal-head"><h3>${labels[key]}</h3><b>${value.sub_score}</b></div><div class="track"><i style="width:${value.sub_score}%"></i></div><p>${esc(value.note)}</p></article>`).join("");
  $("#results").innerHTML=`<div class="score-card"><div class="score-copy"><h2>${esc(data.verdict)}</h2><p>Six clear signals, evaluated for this opportunity.</p></div><div class="score">${data.worth_score}<small>OUT OF 100</small></div></div><h2 class="posting-title">${esc(posting.title || "Your internship")}${posting.company ? ` <span>at ${esc(posting.company)}</span>` : ""}</h2><div class="breakdown">${items}</div>`;
  $("#results").classList.remove("hidden"); $("#results").scrollIntoView({behavior:"smooth",block:"start"});
}
async function request(path, payload) {
  setLoading(true); $("#error").classList.add("hidden"); $("#results").classList.add("hidden");
  try { const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}); const data=await response.json(); if(!response.ok) throw new Error(data.detail || "Something went wrong. Please try manual entry."); displayResults(data); }
  catch(error) { displayError(error.message); } finally { setLoading(false); }
}
async function requestFile(file) {
  setLoading(true); $("#error").classList.add("hidden"); $("#results").classList.add("hidden");
  try { const body=new FormData(); body.append("file",file); const response=await fetch("/score/file",{method:"POST",body}); const data=await response.json(); if(!response.ok) throw new Error(data.detail || "We could not read that file."); displayResults(data); }
  catch(error) { displayError(error.message); } finally { setLoading(false); }
}
$("#url-form").onsubmit = (event) => { event.preventDefault(); request("/score",{url:$("#url").value.trim()}); };
fileForm.onsubmit = (event) => { event.preventDefault(); const file=$("#listing-file").files[0]; if (file) requestFile(file); };
$("#listing-file").onchange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  $("#upload-title").textContent = file.name;
  $("#upload-detail").textContent = `${Math.max(1, Math.round(file.size / 1024))} KB selected — analysing now`;
  requestFile(file);
};
manualForm.onsubmit = (event) => { event.preventDefault(); request("/score/manual",Object.fromEntries(new FormData(manualForm).entries())); };
