import { afterEach, describe, expect, it } from 'vitest'
import { AttachmentId, ImageVariantId } from '@deepseek-ai/dsh-attachment'
import type { AttachmentStore, ImageAttachmentRef, RequestImageAttachment } from '@deepseek-ai/dsh-attachment'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import { DeepSeekAdapter, DeepSeekFileStore, resolveAdapterOptions } from '@deepseek-ai/dsh-llm-deepseek'
import { closeMockServers, mockServer, textEvents } from './mock-server.ts'

/**
 * kline-playbook-engine V0.1 provider-smoke bridge admission.
 *
 * Proves, against the pinned Harness DeepSeek adapter and a local zero-cost
 * mock server, the exact wire invariants of `replay_v0_1_smoke_bridge.ts`:
 *
 * - one governed wake == exactly one model request (no hidden second request);
 * - one wake carries exactly four distinct PNG image uploads + the text block;
 * - a second governed wake issues a second (separate) request;
 * - 5xx and quota/rate-limit failures fail closed with `maxRetries: 0`.
 *
 * No real provider endpoint is contacted; `REAL_DEEPSEEK_PROVIDER_CALLS = 0`.
 */

const PROJECT_PROVIDER = 'deepseek'
const PROJECT_MODEL = 'deepseek-v4-flash-vision-exp'
const TEST_USER_ID = '00000000-0000-4000-8000-000000000001' as never
const PNG_MIME = 'image/png'

function pngBytes(seed: number): Uint8Array {
  // Distinct, deterministic PNG-like byte streams per wake/image.
  const data = new Uint8Array(64)
  for (let index = 0; index < data.length; index += 1) {
    data[index] = (seed * 31 + index * 7 + 1) % 256
  }
  return data
}

function imageRef(seed: number): ImageAttachmentRef {
  const hex = (seed & 0xffff).toString(16).padStart(4, '0')
  return {
    attachmentId: AttachmentId(`sha256:${'0'.repeat(60)}${hex}`),
    mediaType: PNG_MIME,
    bytes: 64,
    width: 8,
    height: 8,
  }
}

function seedOfRef(ref: ImageAttachmentRef): number {
  const text = String(ref.attachmentId)
  const hex = text.slice(text.length - 4)
  return parseInt(hex, 16)
}

function requestImage(seed: number): RequestImageAttachment {
  const ref = imageRef(seed)
  return {
    variantId: ImageVariantId(`sha256:${(seed + 1).toString(16).padStart(64, '0')}`),
    attachment: ref,
    data: pngBytes(seed),
    mediaType: PNG_MIME,
    bytes: 64,
    width: 8,
    height: 8,
    depth: 'uchar',
    space: 'srgb',
    hasAlpha: false,
  }
}

function attachmentStoreOf(): AttachmentStore {
  const readImageRequest = (ref: ImageAttachmentRef): Promise<RequestImageAttachment> =>
    Promise.resolve(requestImage(seedOfRef(ref)))
  return { readImageRequest } as unknown as AttachmentStore
}

async function drain(stream: AsyncIterable<unknown>): Promise<void> {
  for await (const _chunk of stream) { /* drain */ }
}

function wakeMessage(seeds: number[]): ReturnType<typeof createUserMessage> {
  return createUserMessage({
    content: [
      { type: 'text', text: 'deterministic smoke decision prompt + context' },
      ...seeds.map(seed => ({ type: 'image', attachment: imageRef(seed) } as const)),
    ],
    source: { kind: 'plugin', plugin: 'kline-playbook-engine' },
  })
}

interface WirePart {
  type?: string
  file_id?: string
  image_url?: { url?: string }
}

function imagePartIds(request: unknown): string[] {
  const messages = (request as { messages?: Array<{ role?: string; content?: string | WirePart[] }> }).messages ?? []
  const ids: string[] = []
  for (const message of messages) {
    if (Array.isArray(message.content)) {
      for (const part of message.content) {
        if (part.type === 'file' && typeof part.file_id === 'string') ids.push(part.file_id)
        else if (part.type === 'image_url' && part.image_url?.url) ids.push(part.image_url.url)
      }
    }
  }
  return ids
}

async function adapterAt(baseURL: string): Promise<DeepSeekAdapter> {
  const connection = resolveAdapterOptions({
    baseURL,
    models: [{ id: PROJECT_MODEL, inputModalities: ['text', 'image'] }],
    retryPolicy: { mode: 'normal', maxRetries: 0 },
    apiKeyEnv: 'DEEPSEEK_API_KEY',
  })
  return new DeepSeekAdapter({
    options: () => connection,
    resolveApiKey: () => Promise.resolve('test-key'),
    resolveUserId: () => TEST_USER_ID,
    resolveAttachments: () => attachmentStoreOf(),
    resolveFiles: () => new DeepSeekFileStore(),
  })
}

afterEach(async () => {
  await closeMockServers()
})

describe('kline-playbook-engine replay V0.1 provider smoke bridge', () => {
  it('one governed wake emits exactly one chat request carrying four distinct image uploads', async () => {
    const server = await mockServer([{ kind: 'sse', events: textEvents }])
    const adapter = await adapterAt(server.url)
    await drain(adapter.stream({
      provider: PROJECT_PROVIDER,
      model: PROJECT_MODEL,
      system: 'KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_1',
      messages: [wakeMessage([1, 2, 3, 4])],
    }))

    expect(server.requests).toHaveLength(1)
    const imageIds = imagePartIds(server.requests[0])
    expect(imageIds).toHaveLength(4)
    expect(new Set(imageIds).size).toBe(4)
    expect(adapter.providerRetryPolicy(PROJECT_PROVIDER).maxRetries).toBe(0)
  })

  it('a second governed wake issues a second request, never a hidden one', async () => {
    const server = await mockServer([
      { kind: 'sse', events: textEvents },
      { kind: 'sse', events: textEvents },
    ])
    const adapter = await adapterAt(server.url)
    await drain(adapter.stream({
      provider: PROJECT_PROVIDER,
      model: PROJECT_MODEL,
      system: 'KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_1',
      messages: [wakeMessage([11, 12, 13, 14])],
    }))
    await drain(adapter.stream({
      provider: PROJECT_PROVIDER,
      model: PROJECT_MODEL,
      system: 'KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_1',
      messages: [wakeMessage([21, 22, 23, 24])],
    }))

    expect(server.requests).toHaveLength(2)
    expect(imagePartIds(server.requests[0])).toHaveLength(4)
    expect(imagePartIds(server.requests[1])).toHaveLength(4)
    expect(new Set([...imagePartIds(server.requests[0]), ...imagePartIds(server.requests[1])]).size).toBe(8)
  })

  it('fails closed on a provider 5xx with exactly one request (no retry)', async () => {
    const server = await mockServer([
      { kind: 'http-error', status: 500, body: JSON.stringify({ error: { message: 'upstream down' } }) },
    ])
    const adapter = await adapterAt(server.url)
    await expect(drain(adapter.stream({
      provider: PROJECT_PROVIDER,
      model: PROJECT_MODEL,
      system: 'KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_1',
      messages: [wakeMessage([1, 2, 3, 4])],
    }))).rejects.toThrow()
    expect(server.requests).toHaveLength(1)
    expect(adapter.providerRetryPolicy(PROJECT_PROVIDER).maxRetries).toBe(0)
  })

  it('fails closed on a quota/rate-limit response with exactly one request (no retry)', async () => {
    const server = await mockServer([
      { kind: 'http-error', status: 429, body: JSON.stringify({ error: { message: 'rate limit' } }) },
    ])
    const adapter = await adapterAt(server.url)
    await expect(drain(adapter.stream({
      provider: PROJECT_PROVIDER,
      model: PROJECT_MODEL,
      system: 'KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_1',
      messages: [wakeMessage([1, 2, 3, 4])],
    }))).rejects.toThrow()
    expect(server.requests).toHaveLength(1)
  })
})
