import { StytchUIClient } from "@stytch/vanilla-js"

const publicToken = import.meta.env.VITE_STYTCH_PUBLIC_TOKEN
if (!publicToken) {
  console.error("VITE_STYTCH_PUBLIC_TOKEN is not set — Stytch login will not work")
}

export const stytchClient = new StytchUIClient(publicToken ?? "")
