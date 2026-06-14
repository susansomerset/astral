import type { ReportPrimaryAction } from "../lib/recommendedJobReport"

export interface ProfileLink {
  key: string
  label: string
  value: string
  copyable?: boolean
}

interface Props {
  companyName: string
  companyWebsite: string | null
  jobLink: string | null
  jobState: string
  profileLinks: ProfileLink[]
  primaryAction: ReportPrimaryAction | null
  onPrimaryAction: () => void
  primaryBusy: boolean
  stateLabel?: string
  copyFeedback?: string | null
  onCopyLink?: (value: string, linkKey: string) => void
  previewMaterials?: { onClick: () => void }
}

export default function RecommendedJobReportHeader({
  companyName,
  companyWebsite,
  jobLink,
  jobState,
  profileLinks,
  primaryAction,
  onPrimaryAction,
  primaryBusy,
  stateLabel,
  copyFeedback,
  onCopyLink,
  previewMaterials,
}: Props) {
  const applyDisabled =
    primaryAction?.action_key === "apply" && (!jobLink || primaryBusy)

  return (
    <div className="recommended-report-header">
      <div className="recommended-report-header-row">
        {companyWebsite ? (
          <a
            href={companyWebsite}
            target="_blank"
            rel="noopener noreferrer"
            className="recommended-report-company recommended-report-company-link"
          >
            {companyName}
          </a>
        ) : (
          <span className="recommended-report-company">{companyName}</span>
        )}
        <span className="recommended-report-state">
          {stateLabel ?? jobState.replace(/_/g, " ")}
        </span>
      </div>
      {profileLinks.length > 0 && (
        <div className="recommended-report-links">
          {profileLinks.map(link => (
            <button
              key={link.key}
              type="button"
              className="recommended-report-copy-link"
              title={`Copy ${link.label}`}
              onClick={() => onCopyLink?.(link.value, link.key)}
            >
              {link.label}
            </button>
          ))}
          {copyFeedback && (
            <span className="recommended-report-copy-feedback">{copyFeedback}</span>
          )}
        </div>
      )}
      {(previewMaterials || primaryAction) && (
        <div className="recommended-report-header-actions">
          {previewMaterials && (
            <button
              type="button"
              className="modal-btn cancel"
              onClick={previewMaterials.onClick}
            >
              Preview Materials
            </button>
          )}
          {primaryAction && (
            <button
              type="button"
              className={`modal-btn save${primaryBusy ? " in-flight" : ""}`}
              disabled={primaryBusy || applyDisabled}
              onClick={onPrimaryAction}
            >
              {primaryBusy ? "Working…" : primaryAction.label}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
