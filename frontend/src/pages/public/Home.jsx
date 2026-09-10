import AnnouncementSection from '../../components/home/AnnouncementSection'
import ArticleSection from '../../components/home/ArticleSection'
import HomeIntro from '../../components/home/HomeIntro'
import { useHomeContent } from '../../hooks/useHomeContent'
import styles from './Home.module.css'

export default function Home() {
  const { articles, announcements, categories, categoryNames } = useHomeContent()

  return (
    <div className={styles.page}>
      <HomeIntro />
      <AnnouncementSection announcements={announcements} onRetry={announcements.retry} />
      <ArticleSection articles={articles} categoryNames={categoryNames} categoryStatus={categories.status} onRetry={articles.retry} />
    </div>
  )
}
