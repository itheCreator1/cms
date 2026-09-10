import { useCallback, useEffect, useState } from 'react'

export function useAsyncResource(loader, dependencies = []) {
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState({ status: 'loading', data: null, error: null })

  useEffect(() => {
    let active = true
    setState({ status: 'loading', data: null, error: null })
    loader()
      .then((data) => {
        if (active) setState({ status: 'success', data, error: null })
      })
      .catch((error) => {
        if (active) setState({ status: 'error', data: null, error })
      })
    return () => { active = false }
    // The caller declares the values that change the request; the loader is intentionally excluded.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, attempt])

  const retry = useCallback(() => setAttempt((current) => current + 1), [])
  return { ...state, retry }
}
