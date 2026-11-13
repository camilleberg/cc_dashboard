export function createColorbarControl(initialOptions) {
  let options = initialOptions;
  let container;

  function render() {
    if (!container) return;

    container.replaceChildren();

    const label = document.createElement("div");
    label.textContent = options.label;
    label.style.cssText = "font-weight:600;margin-bottom:5px";
    container.appendChild(label);

    const gradient = document.createElement("div");
    gradient.style.cssText = `height:10px;border-radius:2px;background:linear-gradient(to right, ${options.colorStops
      .map(({ color, position }) => `${color} ${position * 100}%`)
      .join(", ")})`;
    container.appendChild(gradient);

    const ticks = document.createElement("div");
    ticks.style.cssText = "display:flex;justify-content:space-between;margin-top:3px;font-size:10px";
    const count = Math.max(2, options.ticks?.count ?? 3);
    for (let index = 0; index < count; index++) {
      const value = options.vmin + ((options.vmax - options.vmin) * index) / (count - 1);
      const tick = document.createElement("span");
      tick.textContent = options.ticks?.format ? options.ticks.format(value) : String(value);
      ticks.appendChild(tick);
    }
    container.appendChild(ticks);
  }

  return {
    onAdd() {
      container = document.createElement("div");
      container.className = "maplibregl-ctrl";
      container.style.cssText =
        "width:180px;padding:8px 10px;border-radius:4px;background:rgba(255,255,255,.95);box-shadow:0 0 0 2px rgba(0,0,0,.1);font:12px/1.3 sans-serif;color:#333;pointer-events:none";
      render();
      return container;
    },
    onRemove() {
      container?.remove();
      container = undefined;
    },
    update(nextOptions) {
      options = nextOptions;
      render();
    }
  };
}
