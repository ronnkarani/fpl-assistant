let selectedPlayers = JSON.parse(localStorage.getItem("selectedPlayers")) || [];
let budget = 1000 - selectedPlayers.reduce((sum, p) => sum + (p.cost * 10), 0);

function selectPlayer(id, cost, team, name, position) {
  if (selectedPlayers.length >= 15) {
    alert("You can only select up to 15 players.");
    return;
  }

  if (selectedPlayers.find(p => p.id === id)) {
    alert(`${name} is already selected.`);
    return;
  }

  const teamCount = selectedPlayers.filter(p => p.team === team).length;
  if (teamCount >= 3) {
    alert(`Only 3 players allowed from ${team}.`);
    return;
  }

  if (budget - (cost * 10) < 0) {
    alert(`Budget exceeded! Cannot add ${name}.`);
    return;
  }

  selectedPlayers.push({ id, name, team, cost, position });
  budget -= cost * 10;
  saveAndUpdateUI();
}

function removePlayer(id) {
  const index = selectedPlayers.findIndex(p => p.id === id);
  if (index > -1) {
    budget += selectedPlayers[index].cost * 10;
    selectedPlayers.splice(index, 1);
    saveAndUpdateUI();
  }
}

function saveAndUpdateUI() {
  localStorage.setItem("selectedPlayers", JSON.stringify(selectedPlayers));
  updateSelectionUI();
  displayBest11();
}

function updateSelectionUI() {
  const budgetInfo = document.getElementById("budget-info");
  const selectedList = document.getElementById("selected-players");

  budgetInfo.textContent = `Budget Remaining: £${(budget / 10).toFixed(1)}M (${selectedPlayers.length}/15 players)`;

  if (selectedPlayers.length === 0) {
    selectedList.innerHTML = "<li>No players selected yet.</li>";
    return;
  }

  selectedList.innerHTML = "";
  selectedPlayers.forEach((p) => {
    const li = document.createElement("li");
    li.innerHTML = `${p.name} (${p.team}, ${p.position}) - £${p.cost.toFixed(1)}M 
      <button onclick="removePlayer(${p.id})">Remove</button>`;
    selectedList.appendChild(li);
  });
}

function displayBest11() {
  const best11List = document.getElementById("best-11");
  if (!best11List) return;

  const best11 = selectedPlayers.slice(0, 11);
  let totalCost = best11.reduce((sum, p) => sum + p.cost, 0);

  if (best11.length === 0) {
    best11List.innerHTML = "<li>No players selected yet.</li>";
    return;
  }

  best11List.innerHTML = "";
  best11.forEach((p) => {
    const li = document.createElement("li");
    li.textContent = `${p.name} (${p.position}, ${p.team}) - £${p.cost.toFixed(1)}M`;
    best11List.appendChild(li);
  });

  const totalLi = document.createElement("li");
  totalLi.innerHTML = `<strong>Total Price: £${totalCost.toFixed(1)}M</strong>`;
  best11List.appendChild(totalLi);
}

document.addEventListener("DOMContentLoaded", () => {
  updateSelectionUI();
  displayBest11();
  enableTableSort();
  setupFilters();
});

// Sorting table by clicking headers
function enableTableSort() {
  document.querySelectorAll("#player-table th").forEach((th, colIndex) => {
    th.addEventListener("click", () => {
      const rows = Array.from(document.querySelectorAll("#player-table tbody tr"));
      const sortedRows = rows.sort((a, b) => {
        const aVal = a.children[colIndex].innerText;
        const bVal = b.children[colIndex].innerText;
        const isNumber = !isNaN(parseFloat(aVal));
        return isNumber ? parseFloat(bVal) - parseFloat(aVal) : aVal.localeCompare(bVal);
      });
      const tbody = document.querySelector("#player-table tbody");
      tbody.innerHTML = "";
      sortedRows.forEach(row => tbody.appendChild(row));
    });
  });
}

// Filter dropdown functionality
function setupFilters() {
  const positionFilter = document.getElementById("filter-position");
  const teamFilter = document.getElementById("filter-team");
  const priceFilter = document.getElementById("filter-price");

  [positionFilter, teamFilter, priceFilter].forEach(filter => {
    filter.addEventListener("change", applyFilters);
  });
}

function applyFilters() {
  const positionVal = document.getElementById("filter-position").value;
  const teamVal = document.getElementById("filter-team").value;
  const priceVal = parseFloat(document.getElementById("filter-price").value);

  document.querySelectorAll("#player-table tbody tr").forEach(row => {
    const position = row.children[2].innerText;
    const team = row.children[1].innerText;
    const price = parseFloat(row.children[3].innerText);

    const matchPosition = positionVal === "All" || position === positionVal;
    const matchTeam = teamVal === "All" || team === teamVal;
    const matchPrice = isNaN(priceVal) || price <= priceVal;

    row.style.display = (matchPosition && matchTeam && matchPrice) ? "" : "none";
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.querySelector(".hamburger");
  const navRight = document.querySelector(".nav-right");
  const dropdownBtn = document.querySelector(".dropbtn");
  const dropdownContent = document.querySelector(".dropdown-content");

  // Toggle mobile menu
  hamburger.addEventListener("click", () => {
    navRight.classList.toggle("show");
  });

  // Toggle dropdown in mobile
  dropdownBtn.addEventListener("click", (e) => {
    e.preventDefault();
    dropdownContent.classList.toggle("show");
  });

  // Close dropdown when clicking outside
  window.addEventListener("click", (e) => {
    if (
      !e.target.matches(".dropbtn") &&
      !e.target.closest(".dropdown-content")
    ) {
      dropdownContent.classList.remove("show");
    }
  });
});


// static/js/stats.js
const topScorersBox = document.getElementById("top-scorers-box");
const topAssistsBox = document.getElementById("top-assists-box");
const injuriesBox = document.getElementById("injuries-box");

function fetchAndUpdateStats() {
  fetch("https://fantasy.premierleague.com/api/bootstrap-static/")
    .then(res => res.json())
    .then(data => {
      const players = data.elements;

      // Top scorers
      const topScorers = [...players]
        .sort((a, b) => b.goals_scored - a.goals_scored)
        .slice(0, 10);
      topScorersBox.innerHTML = topScorers.map(p =>
        `<p>${p.web_name} - ${p.goals_scored} goals</p>`
      ).join("");

      // Top assists
      const topAssists = [...players]
        .sort((a, b) => b.assists - a.assists)
        .slice(0, 10);
      topAssistsBox.innerHTML = topAssists.map(p =>
        `<p>${p.web_name} - ${p.assists} assists</p>`
      ).join("");

      // Injured players
      const injured = players.filter(p => p.status === "i" || p.status === "d").slice(0, 10);
      injuriesBox.innerHTML = injured.map(p =>
        `<p>${p.web_name} - ${p.news || "Injured"}</p>`
      ).join("");
    })
    .catch(error => {
      console.error("Error fetching FPL data:", error);
    });
}

// Fetch immediately, then every 2 minutes
fetchAndUpdateStats();
setInterval(fetchAndUpdateStats, 120000);


// 🔄 Auto-refresh the page every 5 minutes
setInterval(() => {
    window.location.reload();
}, 300000); // 300,000ms = 5 minutes
