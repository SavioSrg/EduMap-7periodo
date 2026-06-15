(function () {
  "use strict";

  const state = {
    objetivo: null,
    interesse: null,
    notas: { matematica: null, humanas: null, natureza: null, linguagens: null, redacao: null },
    grau: null,
    modalidade: null,
  };

  const TOTAL_STEPS = 7;
  let currentStep = 0;

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function showStep(step) {
    $$(".step").forEach((el) => (el.hidden = true));
    const target = $(`.step[data-step="${step}"]`);
    if (target) target.hidden = false;
    if (typeof step === "number") {
      currentStep = step;
      $("#progress-bar").style.width = ((step - 1) / (TOTAL_STEPS - 1)) * 100 + "%";
    }
  }

  function markSelected(group, value) {
    $$(`.options[data-field="${group}"] .option`).forEach((b) => {
      b.classList.toggle("selected", b.dataset.value === value);
    });
  }

  function handleOptionClick(e) {
    const btn = e.target.closest(".option");
    if (!btn) return;
    const group = btn.parentElement.dataset.field;
    const value = btn.dataset.value;
    state[group] = value;
    markSelected(group, value);

    // Avança automaticamente para a próxima etapa após escolher
    setTimeout(() => {
      if (group === "objetivo") showStep(2);
      else if (group === "interesse") showStep(3);
      else if (group === "grau") showStep(5);
      else if (group === "modalidade") {
        renderSummary();
        showStep(6);
      }
    }, 180);
  }

  function validateNotas() {
    const form = $("#form-notas");
    let ok = true;
    ["matematica", "humanas", "natureza", "linguagens", "redacao"].forEach((name) => {
      const input = form.elements[name];
      const v = parseFloat(input.value);
      const valid = Number.isFinite(v) && v >= 0 && v <= 1000;
      input.classList.toggle("invalid", !valid);
      if (valid) state.notas[name] = v;
      else ok = false;
    });
    return ok;
  }

  function renderSummary() {
    const items = [
      ["Objetivo", state.objetivo],
      ["Área de interesse", state.interesse],
      ["Grau", state.grau],
      ["Modalidade", state.modalidade],
      ["Matemática", state.notas.matematica],
      ["Ciências Humanas", state.notas.humanas],
      ["Ciências da Natureza", state.notas.natureza],
      ["Linguagens", state.notas.linguagens],
      ["Redação", state.notas.redacao],
    ];
    $("#summary").innerHTML = items
      .map(([k, v]) => `<li><span>${k}</span><span>${v ?? "—"}</span></li>`)
      .join("");
  }

  function goBack() {
    if (currentStep >= 0) showStep(currentStep - 1);
    if (currentStep == 1) {
      const intro = $(".hero-section");
      const cardSection = $(".card");

      if (intro) intro.hidden = false; 
      if (cardSection) cardSection.hidden = true; 
    }
  }

  async function gerarRecomendacoes() {
    showStep("loading");
    try {
      const res = await fetch(`${window.API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objetivo: state.objetivo,
          interesse: state.interesse,
          grau: state.grau,
          modalidade: state.modalidade,
          notas: state.notas,
        }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Erro ${res.status}: ${text || res.statusText}`);
      }
      const data = await res.json();
      renderResults(data);
      showStep("result");
    } catch (err) {
      $("#error-msg").textContent =
        "Não conseguimos consultar a IA agora. Verifique sua conexão e se a API está disponível. (" +
        (err.message || err) + ")";
      showStep("error");
    }
  }

  function renderResults(data) {
    $("#perfil-text").textContent =
      `Seu perfil possui maior aderência à área de ${data.perfil}.`;
    const list = $("#results");
    list.innerHTML = (data.cursos || [])
      .map((c, i) => `
        <li class="result">
          <div class="result-head">
            <div>
              <div class="result-rank">#${i + 1}</div>
              <div class="result-name">${c.nome}</div>
            </div>
            <div class="result-chance">${c.chance.toFixed(1)}%</div>
          </div>
          <div class="bar"><div class="bar-fill" data-chance="${c.chance}"></div></div>
        </li>`)
      .join("");
    // Anima barras
    requestAnimationFrame(() => {
      $$(".bar-fill").forEach((el) => {
        el.style.width = `${Math.max(2, parseFloat(el.dataset.chance))}%`;
      });
    });
  }

  function reset() {
    state.objetivo = state.interesse = state.grau = state.modalidade = null;
    Object.keys(state.notas).forEach((k) => (state.notas[k] = null));
    $$(".option.selected").forEach((b) => b.classList.remove("selected"));
    const form = $("#form-notas");
    if (form) form.reset();
    showStep(1);
  }

  // Bindings
  document.addEventListener("click", (e) => {
    if (e.target.closest(".options")) return handleOptionClick(e);
    const action = e.target.closest("[data-action]")?.dataset.action;
    if (!action) {
      if (e.target.id === "btn-gerar") return gerarRecomendacoes();
      return;
    }
    if (action === "start-app") {
      // Oculta a seção de introdução para dar foco ao questionário
      const intro = $(".hero-section");
      const cardSection = $(".card");

      if (intro) intro.hidden = true; 
      
      if (cardSection) cardSection.hidden = false; 
      showStep(1);
      return;
    }
    if (action === "back") return goBack();
    if (action === "next-notas") {
      if (validateNotas()) showStep(4);
      return;
    }
    if (action === "retry") {
      renderSummary();
      showStep(6);
      return;
    }
    if (action === "restart") return reset();
  });

  // showStep(1);
})();