import Modal from "./Modal"

interface Props {
  open: boolean
  onClose: () => void
  vector: string
  content: string | null
}

export default function RubricModal({ open, onClose, vector, content }: Props) {
  return (
    <Modal open={open} onClose={onClose} title={`Rubric — ${vector}`} stacked>
      <div className="entity-jd-content">
        {content ?? "No rubric found for this vector."}
      </div>
    </Modal>
  )
}
