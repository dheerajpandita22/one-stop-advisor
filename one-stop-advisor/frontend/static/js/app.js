// Quiz submit
const quizForm = document.getElementById("quiz-form");
if (quizForm) {
  quizForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(quizForm);
    const interests = ["Realistic","Investigative","Artistic","Social","Enterprising","Conventional"]
      .reduce((acc,k)=>{ acc[k]=parseFloat(fd.get(k)||0.5); return acc; },{});
    const payload = {
      name: fd.get("name"),
      grade: fd.get("grade"),
      interests: interests,
      profile: {
        location: fd.get("location"),
        budget: fd.get("budget") ? parseInt(fd.get("budget")) : null
      }
    };
    const res = await fetch("/api/quiz", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    const userId = data.user_id;
    const type = payload.grade === "10" ? "stream" : "career";
    window.location.href = `/results?user_id=${userId}&type=${type}`;
  });
}

// Manual marks submit
const marksForm = document.getElementById("marks-form");
if (marksForm) {
  marksForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(marksForm);
    const userId = fd.get("user_id");
    const res = await fetch("/api/marks",{method:"POST", body: fd});
    const data = await res.json();
    const type = data.streams ? "stream" : "career";
    window.location.href = `/results?user_id=${userId}&type=${type}`;
  });
}

// Upload marksheet (OCR)
const uploadForm = document.getElementById("upload-form");
if (uploadForm) {
  uploadForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(uploadForm);
    const userId = fd.get("user_id");
    const res = await fetch("/api/marks",{method:"POST", body: fd});
    const data = await res.json();
    const type = data.streams ? "stream" : "career";
    window.location.href = `/results?user_id=${userId}&type=${type}`;
  });
}

// College search
const collegeForm = document.getElementById("college-search");
if (collegeForm) {
  collegeForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(collegeForm);
    const params = new URLSearchParams();
    for (const [k,v] of fd.entries()) if (v) params.append(k,v);
    const res = await fetch("/api/colleges?"+params.toString());
    const data = await res.json();
    const list = document.getElementById("college-list");
    list.innerHTML = data.map(c=>`<li><b>${c.name}</b> — ${c.district} | Fees/yr ₹${c.fees_per_year}</li>`).join("");
  });
}

// Advisor chat
const chatForm = document.getElementById("chat-form");
if (chatForm) {
  chatForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(chatForm);
    const res = await fetch("/api/advisor",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({user_id: fd.get("user_id"), message: fd.get("message")})
    });
    const data = await res.json();
    document.getElementById("chat-answer").textContent = data.answer + (data.sources?.length ? `\nSources: ${data.sources.join(", ")}` : "");
  });
}

// Human escalation
const humanForm = document.getElementById("human-form");
if (humanForm) {
  humanForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const fd = new FormData(humanForm);
    const res = await fetch("/api/escalate",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({user_id: fd.get("user_id"), note: fd.get("note")})
    });
    const data = await res.json();
    document.getElementById("human-status").textContent = data.message;
  });
}