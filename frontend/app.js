
const API = "http://127.0.0.1:5000/api";
const $ = (id) => document.getElementById(id);

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `Erro HTTP ${response.status}`);
  }

  return data;
}

function showFeedback(message, isError = false) {
  $("feedback").textContent = message;
  $("feedback").style.color = isError ? "#b42318" : "#18794e";
}

async function refreshStatus() {
  try {
    const [health, status] = await Promise.all([
      request("/health"),
      request("/status")
    ]);

    $("connection").textContent =
      health.api === "ok" ? "API conectada" : "API indisponível";

    $("barrierState").textContent =
      status.barrier_state || "Aguardando dados";

    $("mode").textContent = status.mode || "—";

    $("distance").textContent =
      status.distance_cm == null
        ? "—"
        : `${Number(status.distance_cm).toFixed(1)} cm`;

    $("presence").textContent =
      status.presence_detected ? "Detectada" : "Não detectada";

  } catch (error) {
    $("connection").textContent = "API desconectada";
    $("feedback").textContent =
      `Não foi possível consultar a API: ${error.message}`;
  }
}

async function refreshEvents() {
  try {
    const events = await request("/events?limit=30");
    const body = $("events");

    body.replaceChildren();

    if (!events.length) {
      body.innerHTML =
        '<tr><td colspan="5">Nenhum evento registrado.</td></tr>';
      return;
    }

    for (const event of events) {
      const tr = document.createElement("tr");

      const values = [
        new Date(event.created_at).toLocaleString("pt-BR"),
        event.event_type,
        event.message,
        event.distance_cm == null ? "—" : `${event.distance_cm} cm`,
        event.barrier_state || "—"
      ];

      for (const value of values) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      }

      body.appendChild(tr);
    }

  } catch (error) {
    showFeedback(
      `Falha ao carregar histórico: ${error.message}`,
      true
    );
  }
}

// Comandos de controle da cancela
document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      const result = await request("/commands", {
        method: "POST",
        body: JSON.stringify({
          action: button.dataset.command
        })
      });

      showFeedback(result.message || "Comando enviado.");
      await refreshEvents();

    } catch (error) {
      showFeedback(error.message, true);
    }
  });
});

// Simulação de leitura
$("simulate").addEventListener("click", async () => {
  const distance = Number($("demoDistance").value);

  try {
    await request("/telemetry", {
      method: "POST",
      body: JSON.stringify({
        distance_cm: distance,
        presence_detected: distance <= 25,
        barrier_state: distance <= 25 ? "OPEN" : "CLOSED",
        mode: "MANUAL"
      })
    });

    showFeedback("Leitura simulada salva no banco.");

    await refreshStatus();
    await refreshEvents();

  } catch (error) {
    showFeedback(error.message, true);
  }
});

// Botão de atualização manual
$("refresh").addEventListener("click", async () => {
  await refreshStatus();
  await refreshEvents();
});

// Primeira atualização
refreshStatus();
refreshEvents();

// Atualizações automáticas controladas
setInterval(refreshStatus, 3000);
setInterval(refreshEvents, 15000);
