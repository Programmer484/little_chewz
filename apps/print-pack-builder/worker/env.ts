export interface Env {
  ASSETS: Fetcher;
  /** "disabled" (default), "demo" or "drive". Anything else is treated as "disabled". */
  RESOURCE_MODE?: string;
  /** Cloudflare Access team domain, e.g. "littlechewz.cloudflareaccess.com". */
  ACCESS_TEAM_DOMAIN?: string;
  /** Cloudflare Access application audience (AUD) tag. */
  ACCESS_AUD?: string;
  /** Secret: Google service-account key JSON with read-only Drive access. */
  GOOGLE_SERVICE_ACCOUNT_JSON?: string;
  /** "true" lets drive mode run on localhost without Cloudflare Access (local testing only). */
  LOCAL_DRIVE_TESTING?: string;
}
