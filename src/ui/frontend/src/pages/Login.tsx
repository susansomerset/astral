import { StytchLogin } from "@stytch/react"
import { Products } from "@stytch/vanilla-js"

const redirect = `${window.location.origin}/authenticate`

const stytchLoginConfig = {
  products: [Products.emailMagicLinks, Products.oauth],
  emailMagicLinksOptions: {
    loginRedirectURL: redirect,
    loginExpirationMinutes: 60,
    signupRedirectURL: redirect,
    signupExpirationMinutes: 60,
  },
  oauthOptions: {
    providers: [{ type: "google" as const }],
    loginRedirectURL: redirect,
    signupRedirectURL: redirect,
  },
}

export default function Login() {
  return (
    <div className="content" style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
      <StytchLogin config={stytchLoginConfig} />
    </div>
  )
}
