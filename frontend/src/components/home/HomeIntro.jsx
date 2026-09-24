import styles from './HomeIntro.module.css'
import typography from '../ui/Typography.module.css'
import { defaultSettings } from '../../services/settings'

export default function HomeIntro({ settings = defaultSettings }) {
  return <section className={styles.intro}><p className={styles.eyebrow}>Independent publishing</p><h1 className={typography.pageTitle}>{settings.homepage_headline}</h1><p>{settings.homepage_intro}</p></section>
}
