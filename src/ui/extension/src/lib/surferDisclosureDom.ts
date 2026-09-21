/**
 * Plain-DOM Surfer disclosure panel (AST-1237).
 * Shell/gate must call needsDisclosure → mountSurferDisclosure before capture (AST-1170 / AST-1238).
 * No network I/O here — onOptIn runs optInSurferConsent in the caller.
 */

import type { SurferConsentDto } from "./surferConsent"

const PANEL_STYLE = `
.astral-surfer-consent-panel {
  font-family: system-ui, sans-serif;
  max-width: 28rem;
  padding: 1.25rem 1.5rem;
  color: #1a1523;
  background: #f7f4fb;
  border: 1px solid #d4cce0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(15, 11, 24, 0.18);
}
.astral-surfer-consent-title {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}
.astral-surfer-consent-body p {
  margin: 0 0 0.75rem;
  font-size: 0.9375rem;
  line-height: 1.45;
}
.astral-surfer-consent-body p:last-child { margin-bottom: 0; }
.astral-surfer-consent-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}
.astral-surfer-consent-opt-in,
.astral-surfer-consent-decline {
  font: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.5rem 0.9rem;
  border-radius: 6px;
  cursor: pointer;
}
.astral-surfer-consent-opt-in {
  border: none;
  color: #fff;
  background: #5b3d8f;
}
.astral-surfer-consent-decline {
  border: 1px solid #b8a9cc;
  color: #3d3550;
  background: transparent;
}
`

function appendCopyParagraphs(body: HTMLElement, copy: string): void {
  for (const block of copy.split("\n\n")) {
    const p = document.createElement("p")
    const lines = block.split("\n")
    lines.forEach((line, i) => {
      if (i > 0) p.appendChild(document.createElement("br"))
      p.appendChild(document.createTextNode(line))
    })
    body.appendChild(p)
  }
}

export function mountSurferDisclosure(
  host: HTMLElement,
  dto: SurferConsentDto,
  handlers: { onOptIn: () => void | Promise<void>; onDecline: () => void },
): { unmount: () => void } {
  // Reuse an existing open shadow root so remount does not throw NotSupportedError.
  const root: HTMLElement | ShadowRoot =
    host.shadowRoot ??
    (typeof host.attachShadow === "function" ? host.attachShadow({ mode: "open" }) : host)
  root.replaceChildren()

  if (root instanceof ShadowRoot) {
    const style = document.createElement("style")
    style.textContent = PANEL_STYLE
    root.appendChild(style)
  }

  const panel = document.createElement("div")
  panel.className = "astral-surfer-consent-panel"

  const title = document.createElement("h2")
  title.className = "astral-surfer-consent-title"
  title.textContent = dto.disclosure_title
  panel.appendChild(title)

  const body = document.createElement("div")
  body.className = "astral-surfer-consent-body"
  appendCopyParagraphs(body, dto.disclosure_copy)
  panel.appendChild(body)

  const actions = document.createElement("div")
  actions.className = "astral-surfer-consent-actions"

  const optIn = document.createElement("button")
  optIn.type = "button"
  optIn.className = "astral-surfer-consent-opt-in"
  optIn.textContent = dto.opt_in_label
  optIn.addEventListener("click", () => {
    void handlers.onOptIn()
  })

  const decline = document.createElement("button")
  decline.type = "button"
  decline.className = "astral-surfer-consent-decline"
  decline.textContent = dto.decline_label
  decline.addEventListener("click", () => {
    handlers.onDecline()
  })

  actions.appendChild(optIn)
  actions.appendChild(decline)
  panel.appendChild(actions)
  root.appendChild(panel)

  return {
    unmount() {
      root.replaceChildren()
    },
  }
}
