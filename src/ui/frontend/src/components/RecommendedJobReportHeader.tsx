interface Props {
  jobTitle: string
  jobLink: string | null
  companyName: string
  companyWebsite: string | null
  applicationEmail: string | null
  linkedInUrl: string | null
  copyFeedback?: string | null
  onCopyApplicationEmail?: () => void
  onCopyLinkedIn?: () => void
  onCopySnapshot?: () => void
  snapshotCopied?: boolean
  snapshotCopying?: boolean
  showPrintResume: boolean
  showPrintCover: boolean
  onPrintResume?: () => void
  onPrintCover?: () => void
}

/** Sticky Recommended Job Report header — deeplinks, copy, print (AST-948). */
export default function RecommendedJobReportHeader({
  jobTitle,
  jobLink,
  companyName,
  companyWebsite,
  applicationEmail,
  linkedInUrl,
  copyFeedback,
  onCopyApplicationEmail,
  onCopyLinkedIn,
  onCopySnapshot,
  snapshotCopied,
  snapshotCopying,
  showPrintResume,
  showPrintCover,
  onPrintResume,
  onPrintCover,
}: Props) {
  const link = jobLink?.trim() || null

  return (
    <div className="recommended-report-header">
      <div className="recommended-report-header-row">
        {link ? (
          <a
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className="recommended-report-title-link"
          >
            {jobTitle}
          </a>
        ) : (
          <span className="recommended-report-title">{jobTitle}</span>
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
      {(onCopySnapshot || applicationEmail || linkedInUrl) && (
        <div className="recommended-report-links">
          {onCopySnapshot && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => onCopySnapshot()}
              disabled={snapshotCopying}
            >
              {snapshotCopied ? "Copied" : "Copy"}
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
          {copyFeedback && (
            <span className="recommended-report-copy-feedback">{copyFeedback}</span>
          )}
        </div>
      )}
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
