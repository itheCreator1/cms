import ContentList from './ContentList'
import { announcementService } from '../../services/announcements'
export default function AnnouncementList() { return <ContentList kind="announcement" service={announcementService} publisherScoped statuses={['draft', 'pending_review', 'published']} /> }
