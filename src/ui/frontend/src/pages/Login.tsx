import { StytchLogin } from "@stytch/react"
import { Products } from "@stytch/vanilla-js"
import { getStytchAuthenticateRedirectUrl } from "../lib/stytchRedirect"

export default function Login() {
  const redirect = getStytchAuthenticateRedirectUrl()
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

  return (
    <div className="content" style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
      <StytchLogin config={stytchLoginConfig} />
    </div>
  )
}
