const arrangements = ["Both parents", "Mother only", "Father only", "Neither parent"];

const distribution = {
  "Both parents": 31.3669465751,
  "Mother only": 45.9157140778,
  "Father only": 4.1967972351,
  "Neither parent": 18.5205421119,
};

const contextData = {
  "Both parents": {
    share: 31.3669465751,
    copy:
      "Children in this group lived with both biological parents. Their households showed the highest median income per person and the strongest computer and fixed-internet access.",
    income: 2276.6666667,
    householdSize: 5.3186869905,
    food: 12.0538174083,
    computer: 37.7782798006,
    internet: 32.4657690201,
    rural: 25.9545352723,
  },
  "Mother only": {
    share: 45.9157140778,
    copy:
      "This was the largest living-arrangement group. The surrounding household profile included lower median income per person and more food insufficiency than the both-parent group.",
    income: 925,
    householdSize: 6.8495785818,
    food: 23.3046589025,
    computer: 16.2625993607,
    internet: 13.2130770792,
    rural: 47.2850461189,
  },
  "Father only": {
    share: 4.1967972351,
    copy:
      "This was the smallest group in the sample, so its estimates are generally less precise. The household resource profile fell between the both-parent and other single-care arrangements.",
    income: 1551.6666667,
    householdSize: 6.2723298422,
    food: 22.1878933944,
    computer: 26.4066844428,
    internet: 21.7440080602,
    rural: 37.356639077,
  },
  "Neither parent": {
    share: 18.5205421119,
    copy:
      "Children in this group did not live with either biological parent. This category can include extended-family and other care arrangements, but the GHS does not directly identify adoption.",
    income: 875,
    householdSize: 6.9710673214,
    food: 23.795474286,
    computer: 13.5853067694,
    internet: 8.7827426383,
    rural: 58.5565573139,
  },
};

const metrics = {
  attendance: {
    tab: "School attendance",
    category: "Education",
    title: "School attendance, ages 5-17",
    description:
      "Percentage of children who were attending an educational institution.",
    scale: 100,
    observed: [97.5189310504, 96.98922086, 97.3825012267, 95.4712532181],
    adjusted: [97.1727811931, 97.1267843995, 97.2596545884, 95.8157469475],
    ci: [
      [96.9310485973, 97.9965274835],
      [96.4902900254, 97.4191221561],
      [95.9596422621, 98.313092453],
      [94.6198510393, 96.1933424816],
    ],
    note:
      "Attendance remained high across all groups. Adjustment narrowed some differences, but the neither-parent estimate remained lower.",
  },
  repetition: {
    tab: "Grade repetition",
    category: "Education",
    title: "Grade repetition, applicable learners",
    description:
      "Percentage of applicable learners reported as repeating the same grade.",
    scale: 8,
    observed: [4.2933710717, 5.25717189, 5.0634005332, 6.6056289728],
    adjusted: [4.8864397427, 5.1977902857, 4.5986046241, 5.8919264596],
    ci: [
      [3.6190042542, 5.0867675523],
      [4.7195535264, 5.8522703997],
      [3.5986725295, 7.0805128059],
      [5.7696834358, 7.5529831500],
    ],
    note:
      "Observed repetition was highest among children living with neither parent. The adjusted gap was smaller, showing why household context matters.",
  },
  food: {
    tab: "Food insufficiency",
    category: "Household wellbeing",
    title: "Child food insufficiency",
    description:
      "Percentage of children in households reporting an indicator of insufficient food.",
    scale: 30,
    observed: [12.0538174083, 23.3046589025, 22.1878933944, 23.795474286],
    note:
      "Food insufficiency was around 12% in the both-parent group and roughly 22%–24% in the other living arrangements.",
  },
  grant: {
    tab: "Social grant",
    category: "Social protection",
    title: "Receipt of any social grant",
    description:
      "Percentage of children reported as receiving at least one social grant.",
    scale: 90,
    observed: [46.2479606038, 79.3016412374, 64.5410765747, 80.8304072453],
    note:
      "Grant receipt was highest for the mother-only and neither-parent groups, indicating the importance of social protection in these households.",
  },
  computer: {
    tab: "Computer access",
    category: "Household resources",
    title: "Household computer access",
    description:
      "Percentage of children living in households with access to a computer.",
    scale: 45,
    observed: [37.7782798006, 16.2625993607, 26.4066844428, 13.5853067694],
    note:
      "Computer access differed substantially, with the lowest estimate among children living with neither biological parent.",
  },
  internet: {
    tab: "Fixed internet",
    category: "Household resources",
    title: "Household fixed-internet access",
    description:
      "Percentage of children living in households with fixed internet access.",
    scale: 40,
    observed: [32.4657690201, 13.2130770792, 21.7440080602, 8.7827426383],
    note:
      "Fixed-internet access ranged from about 9% to 32%, revealing a pronounced digital-resource gap.",
  },
};

let activeMetric = "attendance";
let activeMode = "observed";
let activeArrangement = "Mother only";

const formatPercent = (value) => `${value.toFixed(1)}%`;
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    maximumFractionDigits: 0,
  }).format(value);

function renderDistribution() {
  const chart = document.querySelector("#distribution-chart");
  chart.innerHTML = arrangements
    .map(
      (arrangement) => `
        <div class="distribution-item">
          <div class="distribution-label">
            <span>${arrangement}</span>
            <strong>${formatPercent(distribution[arrangement])}</strong>
          </div>
          <div class="distribution-track" aria-hidden="true">
            <span class="distribution-bar" data-width="${distribution[arrangement]}"></span>
          </div>
        </div>
      `,
    )
    .join("");

  requestAnimationFrame(() => {
    chart.querySelectorAll(".distribution-bar").forEach((bar) => {
      bar.style.width = `${bar.dataset.width}%`;
    });
  });
}

function renderMetricTabs() {
  const tabs = document.querySelector("#metric-tabs");
  tabs.innerHTML = Object.entries(metrics)
    .map(
      ([key, metric]) => `
        <button
          class="metric-tab ${key === activeMetric ? "active" : ""}"
          type="button"
          role="tab"
          aria-selected="${key === activeMetric}"
          data-metric="${key}"
        >
          ${metric.tab}
        </button>
      `,
    )
    .join("");

  tabs.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      activeMetric = button.dataset.metric;
      if (!metrics[activeMetric].adjusted) activeMode = "observed";
      renderMetricTabs();
      renderOutcomeChart();
    });
  });
}

function renderOutcomeChart() {
  const metric = metrics[activeMetric];
  const values = metric[activeMode] || metric.observed;
  const chart = document.querySelector("#outcome-chart");
  const switcher = document.querySelector("#mode-switch");

  document.querySelector("#chart-overline").textContent = metric.category;
  document.querySelector("#chart-title").textContent = metric.title;
  document.querySelector("#chart-description").textContent = metric.description;
  document.querySelector("#chart-note").textContent = metric.note;
  switcher.hidden = !metric.adjusted;

  switcher.querySelectorAll("button").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === activeMode);
    button.setAttribute("aria-pressed", button.dataset.mode === activeMode);
  });

  chart.innerHTML = arrangements
    .map((arrangement, index) => {
      const ci =
        activeMode === "observed" && metric.ci
          ? `<span class="ci-label">95% CI ${metric.ci[index][0].toFixed(1)}–${metric.ci[index][1].toFixed(1)}%</span>`
          : `<span class="ci-label">${activeMode === "adjusted" ? "Adjusted point estimate" : "Weighted estimate"}</span>`;
      const width = Math.min((values[index] / metric.scale) * 100, 100);

      return `
        <div class="outcome-row">
          <div class="outcome-label">
            <span>${arrangement}</span>
            <strong>${formatPercent(values[index])}</strong>
          </div>
          <div
            class="outcome-track"
            role="img"
            aria-label="${arrangement}: ${formatPercent(values[index])}"
          >
            <span class="outcome-bar" data-width="${width}"></span>
          </div>
          ${ci}
        </div>
      `;
    })
    .join("");

  const scale = document.querySelector("#chart-scale");
  scale.innerHTML = `<span>0%</span><span>${metric.scale / 2}%</span><span>${metric.scale}%</span>`;

  requestAnimationFrame(() => {
    chart.querySelectorAll(".outcome-bar").forEach((bar) => {
      bar.style.width = `${bar.dataset.width}%`;
    });
  });
}

function renderArrangementTabs() {
  const selector = document.querySelector("#arrangement-selector");
  selector.innerHTML = arrangements
    .map(
      (arrangement) => `
        <button
          class="arrangement-tab ${arrangement === activeArrangement ? "active" : ""}"
          type="button"
          role="tab"
          aria-selected="${arrangement === activeArrangement}"
          data-arrangement="${arrangement}"
        >
          ${arrangement}
        </button>
      `,
    )
    .join("");

  selector.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      activeArrangement = button.dataset.arrangement;
      renderArrangementTabs();
      renderContext();
    });
  });
}

function renderContext() {
  const context = contextData[activeArrangement];
  document.querySelector("#context-title").textContent = activeArrangement;
  document.querySelector("#context-copy").textContent = context.copy;
  document.querySelector("#context-share-value").textContent = formatPercent(
    context.share,
  );

  const metricsContainer = document.querySelector("#context-metrics");
  const cards = [
    ["Median monthly income", formatCurrency(context.income), "per household member"],
    ["Average household size", context.householdSize.toFixed(1), "people"],
    ["Food insufficiency", formatPercent(context.food), "weighted estimate"],
    ["Computer access", formatPercent(context.computer), "weighted estimate"],
    ["Fixed internet", formatPercent(context.internet), "weighted estimate"],
    ["Rural or farm area", formatPercent(context.rural), "weighted estimate"],
  ];

  metricsContainer.innerHTML = cards
    .map(
      ([label, value, note]) => `
        <div class="context-metric">
          <span>${label}</span>
          <strong>${value}</strong>
          <small>${note}</small>
        </div>
      `,
    )
    .join("");
}

document.querySelector("#mode-switch").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-mode]");
  if (!button) return;
  activeMode = button.dataset.mode;
  renderOutcomeChart();
});

renderDistribution();
renderMetricTabs();
renderOutcomeChart();
renderArrangementTabs();
renderContext();
