const API = "http://localhost:8000";

document.getElementById("fitForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const btn = document.getElementById("btn");
  const loading = document.getElementById("loading");
  const results = document.getElementById("results");

  btn.disabled = true;
  results.classList.add("hidden");
  loading.classList.remove("hidden");

  const payload = {
    name: document.getElementById("name").value.trim(),
    age: parseInt(document.getElementById("age").value),
    gender: document.getElementById("gender").value,
    weight_kg: parseFloat(document.getElementById("weight").value),
    height_cm: parseFloat(document.getElementById("height").value),
    goal: document.getElementById("goal").value,
    activity_level: document.getElementById("activity").value,
    training_place: document.getElementById("place").value,
    days_per_week: parseInt(document.getElementById("days").value),
    food_intake: document.getElementById("food").value.trim() || null,
    allergies: document.getElementById("allergies").value.trim() || null
  };

  try {
    const res = await fetch(`${API}/generate-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erreur serveur ${res.status}`);
    }

    const data = await res.json();
    showResults(data);
  } catch (err) {
    alert("Erreur : " + err.message + "\n\nVérifie que le backend tourne sur http://localhost:8000");
  } finally {
    loading.classList.add("hidden");
    btn.disabled = false;
  }
});

function showResults(data) {
  document.getElementById("bmr").textContent = data.bmr;
  document.getElementById("tdee").textContent = data.tdee;
  document.getElementById("target").textContent = data.target_calories;

  document.getElementById("diet").textContent = data.diet_plan;
  document.getElementById("training").textContent = data.training_program;

  const schedule = document.getElementById("schedule");
  schedule.innerHTML = "";
  data.weekly_schedule.forEach(s => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-2";
    li.innerHTML = `<span class="text-emerald-500 mt-0.5">•</span> <span>${s}</span>`;
    schedule.appendChild(li);
  });

  const tips = document.getElementById("tips");
  tips.innerHTML = "";
  data.tips.forEach(t => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-2";
    li.innerHTML = `<span class="text-amber-500">💡</span> <span>${t}</span>`;
    tips.appendChild(li);
  });

  const badge = document.getElementById("sourceBadge");
  if (data.source === "llm") {
    badge.textContent = "Généré par LLM";
    badge.className = "text-xs px-3 py-1 rounded-full bg-green-100 text-green-800";
  } else {
    badge.textContent = "Mode fallback (sans clé API)";
    badge.className = "text-xs px-3 py-1 rounded-full bg-amber-100 text-amber-800";
  }

  document.getElementById("results").classList.remove("hidden");
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}
