import { useEffect, useState } from 'react'

import { fetchAuthenticatedBlob } from '../../services/api'

export default function AuthenticatedImage({ url, alt = '' }) {
  const [objectUrl, setObjectUrl] = useState(null)

  useEffect(() => {
    let active = true
    let temporaryUrl = null
    fetchAuthenticatedBlob(url).then((blob) => {
      temporaryUrl = URL.createObjectURL(blob)
      if (active) setObjectUrl(temporaryUrl)
      else URL.revokeObjectURL(temporaryUrl)
    }).catch(() => { if (active) setObjectUrl(null) })
    return () => {
      active = false
      if (temporaryUrl) URL.revokeObjectURL(temporaryUrl)
    }
  }, [url])

  return objectUrl ? <img src={objectUrl} alt={alt} /> : <span>Loading picture…</span>
}
