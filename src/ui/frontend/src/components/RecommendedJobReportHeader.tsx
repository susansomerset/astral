interface Props {
  jobTitle: string
  /** AST-1694 listing_href — hyperlink target for the job-link line; only http(s) values are linked. */
  jobLink: string | null
  /** Job-link line display text (AST-1873); falls back to jobLink when absent. */
  jobLinkText?: string | null
  companyName: string
  companyWebsite: string | null
  applicationEmail: string | null
  linkedInUrl: string | null
  copyFeedback?: string | null
  onCopyApplicationEmail?: () => void
  onCopyLinkedIn?: () => void
  onCopyDetailLink?: () => void
  detailLinkCopied?: boolean
  onCopySnapshot?: () => void
  snapshotCopied?: boolean
  snapshotCopying?: boolean
  onSkip?: () => void
  skipBusy?: boolean
  showPrintResume: boolean
  showPrintCover: boolean
  onPrintResume?: () => void
  onPrintCover?: () => void
}

/** Sticky Recommended Job Report header — title row with copy/skip buttons, job-link line, print (AST-948, AST-1873). */
export default function RecommendedJobReportHeader({
  jobTitle,
  jobLink,
  jobLinkText,
  companyName,
  companyWebsite,
  applicationEmail,
  linkedInUrl,
  copyFeedback,
  onCopyApplicationEmail,
  onCopyLinkedIn,
  onCopyDetailLink,
  detailLinkCopied,
  onCopySnapshot,
  snapshotCopied,
  snapshotCopying,
  onSkip,
  skipBusy,
  showPrintResume,
  showPrintCover,
  onPrintResume,
  onPrintCover,
}: Props) {
  // Display text prefers the caller's jobLinkText; the href is jobLink only when http(s).
  const link = jobLinkText?.trim() || jobLink?.trim() || null
  const rawHref = jobLink?.trim() ?? ""
  const href = /^https?:\/\//i.test(rawHref) ? rawHref : null

  return (
    <div className="recommended-report-header">
      {/* Title block (left, wraps) and button row (right, no shrink) share one row. */}
      <div className="recommended-report-header-row">
        <div className="recommended-report-title-block">
          <span className="recommended-report-title">{jobTitle}</span>
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
          {companyWebsite ? (
            <a
              href={companyWebsite}
              target="_blank"
              rel="noopener noreferrer"
              className="recommended-report-company-link"
            >
              {companyName}
            </a>
          ) : (
            <span className="recommended-report-company">{companyName}</span>
          )}
        </div>
        {(onCopyDetailLink || onCopySnapshot || applicationEmail || linkedInUrl || onSkip) && (
          <div className="recommended-report-links">
            {onCopyDetailLink && (
              <button
                type="button"
                className="btn secondary"
                onClick={() => onCopyDetailLink()}
              >
                {detailLinkCopied ? "Copied" : "Copy Job Link"}
              </button>
            )}
            {onCopySnapshot && (
              <button
                type="button"
                className="btn secondary"
                onClick={() => onCopySnapshot()}
                disabled={snapshotCopying}
              >
                {snapshotCopied ? "Copied" : "Copy Job JSON"}
              </button>
            )}
            {applicationEmail && (
              <button
                type="button"
                className="btn secondary"
                title="Copy Application Email"
                onClick={() => onCopyApplicationEmail?.()}
              >
                Copy Application Email
              </button>
            )}
            {linkedInUrl && (
              <button
                type="button"
                className="btn secondary"
                title="Copy LinkedIn Profile"
                onClick={() => onCopyLinkedIn?.()}
              >
                Copy LinkedIn Profile
              </button>
            )}
            {onSkip && (
              <button
                type="button"
                className="btn secondary"
                onClick={() => onSkip()}
                disabled={skipBusy}
              >
                Skip this Job
              </button>
            )}
            {copyFeedback && (
              <span className="recommended-report-copy-feedback">{copyFeedback}</span>
            )}
          </div>
        )}
      </div>
      {(showPrintResume || showPrintCover) && (
        <div className="recommended-report-header-actions">
          {showPrintResume && (
            <button type="button" className="btn secondary" onClick={() => onPrintResume?.()}>
              Print Resume
            </button>
          )}
          {showPrintCover && (
            <button type="button" className="btn secondary" onClick={() => onPrintCover?.()}>
              Print Cover Letter
            </button>
          )}
        </div>
      )}
    </div>
  )
}
