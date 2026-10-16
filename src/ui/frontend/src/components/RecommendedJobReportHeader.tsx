import JobTitleText from "./JobTitleText"

interface Props {
  jobTitle: string
  /** AST-1694 listing_href — hyperlink target for the job-link line; only http(s) values are linked. */
  jobLink: string | null
  /** Job-link line display text (AST-1873); falls back to jobLink when absent. */
  jobLinkText?: string | null
  companyName: string
  companyWebsite: string | null
  /** Job created_at / date discovered (ISO). Also used for the company-line m/d/yy. */
  discoveredAt?: string | null
  recommendedAt?: string | null
  appliedAt?: string | null
  onSkip?: () => void
  skipBusy?: boolean
  onApplied?: () => void
  appliedBusy?: boolean
  onGenerateArtifacts?: () => void
  generateBusy?: boolean
}

function formatReportDate(value: string | null | undefined): string | null {
  const raw = value?.trim()
  if (!raw) return null
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return null
  return new Intl.DateTimeFormat("en-US", {
    year: "2-digit",
    month: "numeric",
    day: "numeric",
  }).format(d)
}

/** Sticky Recommended Job Report header — triage actions, company/dates, no Copy/Print (AST-2233). */
export default function RecommendedJobReportHeader({
  jobTitle,
  jobLink,
  jobLinkText,
  companyName,
  companyWebsite,
  discoveredAt,
  recommendedAt,
  appliedAt,
  onSkip,
  skipBusy,
  onApplied,
  appliedBusy,
  onGenerateArtifacts,
  generateBusy,
}: Props) {
  // Display text prefers the caller's jobLinkText; the href is jobLink only when http(s).
  const link = jobLinkText?.trim() || jobLink?.trim() || null
  const rawHref = jobLink?.trim() ?? ""
  const httpHref = /^https?:\/\//i.test(rawHref)
    ? rawHref
    : (link && /^https?:\/\//i.test(link) ? link : null)
  const href = httpHref
  const websiteRaw = companyWebsite?.trim() || null
  const website = websiteRaw
  const websiteHref = websiteRaw
    ? (/^https?:\/\//i.test(websiteRaw) ? websiteRaw : `https://${websiteRaw}`)
    : null
  const discoveredLabel = formatReportDate(discoveredAt)
  const recommendedLabel = formatReportDate(recommendedAt)
  const appliedLabel = formatReportDate(appliedAt)

  return (
    <div className="recommended-report-header">
      <div className="recommended-report-header-row">
        <div className="recommended-report-title-block">
          <span className="recommended-report-title">
            {companyName}
            {discoveredLabel ? ` · ${discoveredLabel}` : ""}
          </span>
          {link && (
            <div className="recommended-report-job-link-text">
              {href ? (
                <a href={href} target="_blank" rel="noopener noreferrer">
                  {link}
                </a>
              ) : (
                link
              )}
            </div>
          )}
          {jobTitle.trim() && (
            <div className="recommended-report-job-title-secondary">
              <JobTitleText title={jobTitle} fallback={jobTitle} />
            </div>
          )}
          {website && websiteHref && (
            <div className="recommended-report-website-line">
              <a
                href={websiteHref}
                target="_blank"
                rel="noopener noreferrer"
                className="recommended-report-website-link"
              >
                {website}
              </a>
            </div>
          )}
          <div className="recommended-report-company-line">
            <span className="recommended-report-company">{companyName}</span>
            {discoveredLabel && (
              <span className="recommended-report-company-date"> · {discoveredLabel}</span>
            )}
          </div>
        </div>
      </div>
      {(onSkip || onApplied || onGenerateArtifacts) && (
        <div className="recommended-report-header-actions">
          {onSkip && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => onSkip()}
              disabled={skipBusy}
            >
              Skip This Job
            </button>
          )}
          {onApplied && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => onApplied()}
              disabled={appliedBusy}
            >
              Applied to this Job
            </button>
          )}
          {onGenerateArtifacts && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => onGenerateArtifacts()}
              disabled={generateBusy}
            >
              Generate Artifacts
            </button>
          )}
        </div>
      )}
      {(discoveredLabel || recommendedLabel || appliedLabel) && (
        <div className="recommended-report-date-strip">
          {discoveredLabel && (
            <span className="recommended-report-date-strip-item">Discovered: {discoveredLabel}</span>
          )}
          {recommendedLabel && (
            <span className="recommended-report-date-strip-item">Recommended: {recommendedLabel}</span>
          )}
          {appliedLabel && (
            <span className="recommended-report-date-strip-item">Applied: {appliedLabel}</span>
          )}
        </div>
      )}
    </div>
  )
}
