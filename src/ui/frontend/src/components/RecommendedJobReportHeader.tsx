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
      {(applicationEmail || linkedInUrl) && (
        <div className="recommended-report-links">
          {applicationEmail && (
            <button
              type="button"
              className="recommended-report-copy-link"
              title="Copy Application Email"
              onClick={() => onCopyApplicationEmail?.()}
            >
              Copy Application Email
            </button>
          )}
          {linkedInUrl && (
            <button
              type="button"
              className="recommended-report-copy-link"
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
            <button type="button" className="modal-btn cancel" onClick={() => onPrintResume?.()}>
              Print Resume
            </button>
          )}
          {showPrintCover && (
            <button type="button" className="modal-btn cancel" onClick={() => onPrintCover?.()}>
              Print Cover Letter
            </button>
          )}
        </div>
      )}
    </div>
  )
}
