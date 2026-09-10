import styles from './Button.module.css'

export default function Button({ children, className = '', type = 'button', variant = 'primary', ...props }) {
  return <button type={type} className={`${styles.button} ${styles[variant]} ${className}`.trim()} {...props}>{children}</button>
}
