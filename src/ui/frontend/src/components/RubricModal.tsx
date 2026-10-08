import Modal from "./Modal"

interface Props {
  open: boolean
  onClose: () => void
  vector: string
  content: string | null
  /** Content fetch in flight — suppresses the not-found fallback (AST-2059). */
  loading?: boolean
}

export default function RubricModal({ open, onClose, vector, content, loading = false }: Props) {
  return (
    <Modal open={open} onClose={onClose} title={`Rubric — ${vector}`} stacked>
      <div className="entity-jd-content">
        {loading ? "Loading rubric…" : (content ?? "No rubric found for this vector.")}
      </div>
    </Modal>
  )
}
