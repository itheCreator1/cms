import ContentEditor from './ContentEditor'
import { pageService } from '../../services/pages'
export default function PageEditor() { return <ContentEditor kind="page" service={pageService} hasSlug /> }
