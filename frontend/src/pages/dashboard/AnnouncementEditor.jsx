import ContentEditor from './ContentEditor'
import { announcementService } from '../../services/announcements'
export default function AnnouncementEditor() { return <ContentEditor kind="announcement" service={announcementService} hasExpiry reviewWorkflow /> }
