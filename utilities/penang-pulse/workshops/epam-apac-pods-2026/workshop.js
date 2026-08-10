(function () {
  const stage = document.getElementById("mapStage");
  if (!stage) return;

  const pins = Array.from(stage.querySelectorAll(".pin"));
  const popovers = Array.from(stage.querySelectorAll(".popover"));
  const listItems = Array.from(document.querySelectorAll(".poi-item"));

  function closeAll() {
    pins.forEach((pin) => {
      pin.setAttribute("aria-expanded", "false");
      pin.classList.remove("is-active");
    });
    popovers.forEach((pop) => pop.classList.remove("is-open"));
    listItems.forEach((item) => item.setAttribute("aria-current", "false"));
  }

  function openByKey(key, options) {
    const toggle = !options || options.toggle !== false;
    const pin = stage.querySelector('[data-pin="' + key + '"]');
    const popId = pin ? pin.getAttribute("aria-controls") : null;
    const pop = popId ? document.getElementById(popId) : null;
    if (!pin || !pop) return;

    const wasOpen = pin.getAttribute("aria-expanded") === "true";
    closeAll();
    if (toggle && wasOpen) return;

    pin.setAttribute("aria-expanded", "true");
    pin.classList.add("is-active");
    pop.classList.add("is-open");
    listItems.forEach((item) => {
      item.setAttribute("aria-current", item.getAttribute("data-pin") === key ? "true" : "false");
    });
  }

  pins.forEach((pin) => {
    pin.addEventListener("click", (event) => {
      event.stopPropagation();
      openByKey(pin.getAttribute("data-pin"));
    });
    pin.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openByKey(pin.getAttribute("data-pin"));
      }
    });
  });

  listItems.forEach((item) => {
    item.addEventListener("click", (event) => {
      event.stopPropagation();
      openByKey(item.getAttribute("data-pin"));
    });
  });

  stage.querySelectorAll(".popover-close").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      closeAll();
    });
  });

  document.addEventListener("click", (event) => {
    const inStage = stage.contains(event.target);
    const inList = event.target.closest(".poi-panel");
    if (!inStage && !inList) closeAll();
    else if (event.target === stage || event.target.classList.contains("map-svg")) closeAll();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAll();
  });

  openByKey("hotel", { toggle: false });
})();
