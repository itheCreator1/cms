export function LoadingState({ message = 'Loading…' }) {
  return <p className="content-state" aria-live="polite">{message}</p>
}

export function EmptyState({ message }) {
  return <p className="content-state content-state--empty">{message}</p>
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="content-state content-state--error" role="alert">
      <p>{message}</p>
      <button type="button" className="text-button" onClick={onRetry}>Try again</button>
    </div>
  )
}
