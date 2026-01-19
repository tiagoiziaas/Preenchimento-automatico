# preenchimento_app/injected_js.py
INJECT_JS = r"""
(() => {
  if (window.__mapperInstalled) return;
  window.__mapperInstalled = true;

  function cssPath(el) {
    if (!el || el.nodeType !== 1) return "";
    if (el.id) return "#" + CSS.escape(el.id);

    const parts = [];
    while (el && el.nodeType === 1 && el !== document.body) {
      let part = el.nodeName.toLowerCase();

      const name = el.getAttribute("name");
      if (name) part += `[name="${name.replace(/"/g, '\\"')}"]`;

      let sibling = el;
      let nth = 1;
      while ((sibling = sibling.previousElementSibling)) {
        if (sibling.nodeName.toLowerCase() === el.nodeName.toLowerCase()) nth++;
      }
      part += `:nth-of-type(${nth})`;

      parts.unshift(part);
      el = el.parentElement;
    }
    return parts.join(" > ");
  }

  function collect(el) {
    const attrs = {};
    for (const a of el.attributes) {
      if (a && a.name) attrs[a.name] = a.value;
    }

    let labelText = "";
    try {
      const id = el.getAttribute("id");
      if (id) {
        const lab = document.querySelector(`label[for="${CSS.escape(id)}"]`);
        if (lab) labelText = (lab.innerText || "").trim();
      }
      if (!labelText) {
        const wrapLabel = el.closest("label");
        if (wrapLabel) labelText = (wrapLabel.innerText || "").trim();
      }
    } catch (e) {}

    return {
      tag: el.tagName.toLowerCase(),
      type: (el.getAttribute("type") || "").toLowerCase(),
      attrs,
      text: (el.innerText || "").trim(),
      labelText,
      cssPath: cssPath(el)
    };
  }

  const badge = document.createElement("div");
  badge.innerHTML = "MAPEAMENTO<br><b>Shift</b>+Clique Esq = FILL<br><b>Ctrl</b>+Clique Esq = CLICK";
  badge.style.position = "fixed";
  badge.style.bottom = "12px";
  badge.style.right = "12px";
  badge.style.zIndex = "2147483647";
  badge.style.padding = "10px 12px";
  badge.style.borderRadius = "12px";
  badge.style.background = "rgba(124, 58, 237, 0.92)";
  badge.style.color = "white";
  badge.style.fontFamily = "Segoe UI, Arial, sans-serif";
  badge.style.fontSize = "12px";
  badge.style.lineHeight = "1.25";
  badge.style.boxShadow = "0 8px 24px rgba(0,0,0,.25)";
  document.documentElement.appendChild(badge);

  document.addEventListener("click", (e) => {
    const isLeftClick = (e.button === 0);
    const isShift = e.shiftKey === true;
    const isCtrl  = e.ctrlKey === true;

    if (!isLeftClick || (!isShift && !isCtrl)) return;

    const el = e.target;
    if (!el) return;

    const payload = collect(el);
    payload.__action = isCtrl ? "click" : "fill";

    e.preventDefault();
    e.stopPropagation();

    console.log("__MAPPER__" + JSON.stringify(payload));

    if (isCtrl) {
      setTimeout(() => {
        try {
          const opts = {
            bubbles: true, cancelable: true, view: window,
            button: 0, buttons: 1,
            ctrlKey: false, shiftKey: false, altKey: false, metaKey: false
          };
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        } catch (err) {}
      }, 0);
    }
  }, true);

  console.log("__MAPPER__" + JSON.stringify({ready:true}));
})();
"""
