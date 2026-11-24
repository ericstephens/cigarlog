import { type ReactNode, useEffect, useRef } from 'react'

interface ModalProps {
  open: boolean
  title: string
  onClose: () => void
  children: ReactNode
}

export function Modal({ open, title, onClose, children }: ModalProps) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (open) {
      if (!el.open) el.showModal()
    } else {
      if (el.open) el.close()
    }
  }, [open])

  // Close on backdrop click
  function handleClick(e: React.MouseEvent<HTMLDialogElement>) {
    if (e.target === ref.current) onClose()
  }

  return (
    <dialog
      ref={ref}
      onClick={handleClick}
      onClose={onClose}
      className="w-full max-w-md rounded-lg border border-zinc-700 bg-zinc-900 p-0 text-white shadow-xl backdrop:bg-black/60"
    >
      <div className="flex items-center justify-between border-b border-zinc-700 px-5 py-4">
        <h2 className="text-base font-semibold">{title}</h2>
        <button
          onClick={onClose}
          className="text-zinc-400 hover:text-white"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <div className="px-5 py-4">{children}</div>
    </dialog>
  )
}
