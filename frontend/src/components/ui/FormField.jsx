import styles from './FormField.module.css'

export default function FormField({ id, label, ...inputProps }) {
  return <label className={styles.field} htmlFor={id}>{label}<input id={id} {...inputProps} /></label>
}
