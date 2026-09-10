import styles from './HomeIntro.module.css'
import typography from '../ui/Typography.module.css'

export default function HomeIntro() {
  return <section className={styles.intro}><p className={styles.eyebrow}>Independent publishing</p><h1 className={typography.pageTitle}>Stories that keep us connected.</h1><p>News, notices, and voices from across the community.</p></section>
}
