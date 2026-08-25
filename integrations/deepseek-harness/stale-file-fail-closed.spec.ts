import { afterEach, describe, expect, it, vi } from 'vitest'
import { AttachmentId, ImageVariantId } from '@deepseek-ai/dsh-attachment'
import type { AttachmentStore, ImageAttachmentRef, RequestImageAttachment } from '@deepseek-ai/dsh-attachment'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import * as LlmDeepSeek from '@deepseek-ai/dsh-llm-deepseek'
import { DeepSeekAdapter, resolveAdapterOptions } from '@deepseek-ai/dsh-llm-deepseek'

const TEST_USER_ID = '00000000-0000-4000-8000-000000000001' as never

const imageRef: ImageAttachmentRef = {
  attachmentId: AttachmentId(`sha256:${'a'.repeat(64)}`),
  mediaType: 'image/png',
  bytes: 3,
  width: 1,
  height: 1,
}

function requestImage(ref = imageRef): RequestImageAttachment {
  return {
    variantId: ImageVariantId(`sha256:${'b'.repeat(64)}`),
    attachment: ref,
    data: Uint8Array.of(1, 2, 3),
    mediaType: 'image/png',
    bytes: 3,
    width: 1,
    height: 1,
    depth: 'uchar',
    space: 'srgb',
    hasAlpha: true,
  }
}

function fileReference(fileId: string): Awaited<ReturnType<LlmDeepSeek.DeepSeekFileStore['ensureUploaded']>> {
  return {
    record: { fileId: LlmDeepSeek.DeepSeekFileId(fileId) },
    uploaded: true,
  } as Awaited<ReturnType<LlmDeepSeek.DeepSeekFileStore['ensureUploaded']>>
}

async function drain(stream: AsyncIterable<unknown>): Promise<void> {
  for await (const _chunk of stream) { /* drain */ }
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('kline-playbook-engine DeepSeek transport policy', () => {
  it('fails closed on a stale file reference without issuing a hidden second chat request', async () => {
    const readImageRequest = vi.fn((ref: ImageAttachmentRef) => Promise.resolve(requestImage(ref)))
    const attachments = { readImageRequest } as unknown as AttachmentStore
    const ensureUploaded = vi.fn(() => Promise.resolve(fileReference('file-api-stale')))
    const invalidate = vi.fn(() => Promise.resolve())
    const files = { ensureUploaded, invalidate } as unknown as LlmDeepSeek.DeepSeekFileStore

    const connection = resolveAdapterOptions({
      baseURL: 'https://deepseek.invalid',
      models: [{ id: 'deepseek-v4-flash-vision-exp', inputModalities: ['text', 'image'] }],
      retryPolicy: { mode: 'normal', maxRetries: 0 },
    })
    const adapter = new DeepSeekAdapter({
      options: () => connection,
      resolveApiKey: () => Promise.resolve('test-key'),
      resolveUserId: () => TEST_USER_ID,
      resolveAttachments: () => attachments,
      resolveFiles: () => files,
    })

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      error: { message: 'file_id file-api-stale expired' },
    }), {
      status: 400,
      headers: { 'content-type': 'application/json' },
    }))

    await expect(drain(adapter.stream({
      provider: 'deepseek-official',
      model: 'deepseek-v4-flash-vision-exp',
      messages: [createUserMessage({
        content: [{ type: 'image', attachment: imageRef }],
        source: { kind: 'plugin', plugin: 'kline-playbook-engine' },
      })],
    }))).rejects.toMatchObject({ code: 'INVALID_REQUEST' })

    expect(adapter.providerRetryPolicy('deepseek-official').maxRetries).toBe(0)
    expect(readImageRequest).toHaveBeenCalledTimes(1)
    expect(ensureUploaded).toHaveBeenCalledTimes(1)
    expect(invalidate).toHaveBeenCalledTimes(1)
    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })
})
