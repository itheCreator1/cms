import { useState } from 'react'

import Button from '../../components/ui/Button'
import { ErrorState, LoadingState } from '../../components/ui/ContentState'
import typography from '../../components/ui/Typography.module.css'
import styles from './Management.module.css'
import { useAsyncResource } from '../../hooks/useAsyncResource'
import { settingsService } from '../../services/settings'

const fields = [
  ['site_name', 'Site name', 120], ['tagline', 'Tagline', 160],
  ['homepage_headline', 'Homepage headline', 180], ['homepage_intro', 'Homepage intro', 2000],
]

function SettingsForm({ values, onSaved }) {
  const [form, setForm] = useState(values)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const save = async (event) => {
    event.preventDefault(); setSaving(true); setError('')
    try { const result = await settingsService.update(form); setForm(result); onSaved() }
    catch (failure) { setError(failure.message) }
    finally { setSaving(false) }
  }
  return <form className={styles.form} onSubmit={save}>{fields.map(([key, label, maxLength]) => <label key={key}>{label}{key === 'homepage_intro' ? <textarea value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} maxLength={maxLength} /> : <input value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} maxLength={maxLength} />}</label>)}<Button type="submit" disabled={saving}>Save settings</Button>{error && <p role="alert">{error}</p>}</form>
}

export default function ManageSettings() {
  const resource = useAsyncResource(settingsService.get)
  return <section className={styles.page}><h1 className={typography.pageTitle}>Site settings</h1>
    {resource.status === 'loading' && <LoadingState message="Loading settings…" />}
    {resource.status === 'error' && <ErrorState message={resource.error.message} onRetry={resource.retry} />}
    {resource.status === 'success' && <SettingsForm values={resource.data} onSaved={() => window.dispatchEvent(new Event('cms-settings-updated'))} />}
  </section>
}
