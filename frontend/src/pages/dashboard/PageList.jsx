import ContentList from './ContentList'
import { pageService } from '../../services/pages'
export default function PageList() { return <ContentList kind="page" service={pageService} statuses={['draft', 'published']} /> }
