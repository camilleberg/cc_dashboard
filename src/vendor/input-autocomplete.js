// source: https://observablehq.com/@floatingpurr/input-autocomplete
import * as htl from "npm:htl";
import * as d3 from "npm:d3";

export function SearchForm({
  uid = crypto.randomUUID(),
  placeholder = "",
  description = "",
  format = (d) => d,
  suggestion = () => [],
  defaultValue = ""
} = {}) {
  const input = htl.html`<input 
        type="text"
        placeholder="${placeholder}" 
        list="${uid}"
        autocomplete="off"
      >`;

  const tag = htl.html`<div style="font-size: 0.85rem; font-style: italic; margin-top: 3px;">${description}</div>`;

  const datalist = htl.html`<datalist id="${uid}">`;

  const form = htl.html`<div>${input}${tag}${datalist}`;

  let results = [];

  form.value = defaultValue;
  form.onsubmit = (event) => event.preventDefault();

  form.onchange = (event) => {
    const value = event.target.value;
    form.value = results.find((d) => format(d) == value) || "";
    input.blur();
    form.dispatchEvent(new CustomEvent("input"));
  };

  const options = new Map();

  const getOption = async (text) =>
    options.get(text) ||
    (text ? options.set(text, await suggestion(text)) : options.set(text, []),
    options.get(text));

  input.oninput = async (event) => {
    let value = event.target.value;
    results = await getOption(value);

    d3.select(`#${uid}`)
      .selectAll("option")
      .data(results)
      .join("option")
        .attr("value", format);
  };

  if (defaultValue) {
    form.dispatchEvent(new CustomEvent("input"));
    form.querySelector('input').value = defaultValue;
  }

  return form;
}