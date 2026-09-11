import PlainTextBody from './PlainTextBody'
import { resolveApiUrl } from '../../services/api'

export default function BodyBlocks({ blocks, body }) {
  if (!blocks?.length) return <PlainTextBody body={body} />
  return (
    <div>
      {blocks.map((block, index) => block.type === 'text'
        ? <PlainTextBody key={`text-${index}`} body={block.text} />
        : <img key={`image-${index}`} src={resolveApiUrl(block.media?.url)} alt={block.media?.alt_text || ''} />)}
    </div>
  )
}
