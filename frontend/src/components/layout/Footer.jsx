import styles from './Footer.module.css'

export default function Footer({ settings }) {
  return <footer className={styles.footer}><span>{settings.site_name}</span><span>{settings.tagline}</span></footer>
}
