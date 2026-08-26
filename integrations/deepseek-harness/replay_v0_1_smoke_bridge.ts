#!/usr/bin/env tsx
/**
 * One-shot DeepSeek provider bridge for the V0.1 replay provider-smoke slot.
 *
 * This bridge is deliberately NOT an agent loop.  One governed wake maps to
 * exactly one call of the pinned Harness's one-shot model-stream API
 * (`adapter.stream()`, the same one-shot API used by the Harness admission
 * tests; it is the current equivalent of `ctx.llm.stream()`).  There is no
 * session-title call, no compaction call, no retry, no tool-loop second call
 * and no hidden stale-file retry.  The project fail-closed transport patch
 * (`NO_HIDDEN_STALE_CHAT_RETRY`, maxRetries: 0) is assumed applied to the
 * pinned Harness checkout.
 *
 * Usage (run from the pinned Harness checkout with `tsx`):
 *   tsx replay_v0_1_smoke_bridge.ts --bundle <request.json> --out <result.json>
 *
 * The bridge never reads or logs secrets; the API key is resolved from the
 * environment and is never written to the evidence output.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { AttachmentId, ImageVariantId, AttachmentStore } from '@deepseek-ai/dsh-attachment'
import type {
  ImageAttachmentLimits,
  ImageAttachmentRef,
  ImageRequestPolicy,
  RequestImageAttachment,
  SaveImageAttachment,
  StoredImageAttachment,
} from '@deepseek-ai/dsh-attachment'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import { DeepSeekAdapter, DeepSeekFileStore, resolveAdapterOptions } from '@deepseek-ai/dsh-llm-deepseek'

const PROVIDER = 'deepseek'
const PNG_MIME = 'image/png'

interface BundleImage {
  path: string
  sha256: string
  width: number
  height: number
}

interface Bundle {
  provider: string
  model: string
  system: string
  decision: string
  contextJson: string
  images: BundleImage[]
  baseURL?: string
  apiKeyEnv?: string
}

function parseArgs(argv: string[]): { bundle: string; out: string } {
  let bundle: string | undefined
  let out: string | undefined
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--bundle') bundle = argv[i + 1]
    else if (argv[i] === '--out') out = argv[i + 1]
  }
  if (!bundle || !out) throw new Error('usage: tsx replay_v0_1_smoke_bridge.ts --bundle <json> --out <json>')
  return { bundle, out }
}

function bundleAttachmentStore(images: Array<{ sha256: string; data: Uint8Array; width: number; height: number }>): AttachmentStore {
  const byId = new Map<string, { data: Uint8Array; width: number; height: number; sha256: string }>()
  for (const image of images) byId.set(`sha256:${image.sha256}`, image)
  const imageLimits: ImageAttachmentLimits = {
    maxImageBytes: 20 * 1024 * 1024,
    maxImagesPerMessage: 16,
    maxMessageImageBytes: 80 * 1024 * 1024,
    maxImagePixels: 8192 * 8192,
    maxImageDimension: 8192,
    mediaTypes: ['image/png'],
  }
  return {
    imageLimits,
    async validateImage(_input: SaveImageAttachment): Promise<void> {
      // Bundle images come from the deterministic project renderer; the
      // provider boundary re-checks media type and bounds.
      return
    },
    async saveImage(_input: SaveImageAttachment): Promise<ImageAttachmentRef> {
      throw new Error('bundle attachment store is read-only for the smoke bridge')
    },
    async readImage(ref: ImageAttachmentRef, _signal?: AbortSignal): Promise<StoredImageAttachment> {
      const image = byId.get(String(ref.attachmentId))
      if (!image) throw new Error(`bundle attachment store is missing ${String(ref.attachmentId)}`)
      return { ref, data: image.data }
    },
    async readImageRequest(ref: ImageAttachmentRef, _policy: ImageRequestPolicy, _signal?: AbortSignal): Promise<RequestImageAttachment> {
      const image = byId.get(String(ref.attachmentId))
      if (!image) throw new Error(`bundle attachment store is missing ${String(ref.attachmentId)}`)
      return {
        variantId: ImageVariantId(`sha256:${image.sha256}`),
        attachment: ref,
        data: image.data,
        mediaType: PNG_MIME,
        bytes: image.data.byteLength,
        width: image.width,
        height: image.height,
        depth: 'uchar',
        space: 'srgb',
        hasAlpha: false,
      }
    },
  } as unknown as AttachmentStore
}

function imageRef(image: BundleImage): ImageAttachmentRef {
  return {
    attachmentId: AttachmentId(`sha256:${image.sha256}`),
    mediaType: PNG_MIME,
    bytes: 0, // corrected by the attachment store's request projection
    width: image.width,
    height: image.height,
  }
}

async function main(): Promise<number> {
  const { bundle: bundlePath, out: outPath } = parseArgs(process.argv.slice(2))
  const bundleText = readFileSync(bundlePath, 'utf8').replace(/^\uFEFF/, '')
  const raw = JSON.parse(bundleText) as Record<string, unknown>
  if (!raw || typeof raw !== 'object') throw new Error('bundle must be a JSON object')
  const provider = String(raw.provider ?? PROVIDER)
  const model = String(raw.model ?? '')
  const system = String(raw.system ?? '')
  const decision = String(raw.decision ?? '')
  const contextJson = String(raw.contextJson ?? '')
  const apiKeyEnv = String(raw.apiKeyEnv ?? 'DEEPSEEK_API_KEY')
  const baseURL = typeof raw.baseURL === 'string' && raw.baseURL.length > 0 ? raw.baseURL : undefined
  const imagesRaw = Array.isArray(raw.images) ? (raw.images as BundleImage[]) : []
  if (imagesRaw.length !== 4) throw new Error('one provider smoke request must carry exactly four PNG images')

  const images: Array<{ sha256: string; data: Uint8Array; width: number; height: number }> = []
  const refs: ImageAttachmentRef[] = []
  for (const image of imagesRaw) {
    const data = new Uint8Array(readFileSync(resolve(image.path)))
    images.push({ sha256: image.sha256, data, width: image.width, height: image.height })
    refs.push(imageRef(image))
  }

  const apiKey = process.env[apiKeyEnv]
  if (!apiKey || apiKey.length === 0) {
    throw new Error(`provider smoke bridge requires ${apiKeyEnv} in the environment`)
  }

  const attachments = bundleAttachmentStore(images)
  const connection = resolveAdapterOptions({
    ...(baseURL ? { baseURL } : {}),
    models: [{ id: model, inputModalities: ['text', 'image'] }],
    retryPolicy: { mode: 'normal', maxRetries: 0 },
    apiKeyEnv,
  })
  const adapter = new DeepSeekAdapter({
    options: () => connection,
    resolveApiKey: async () => apiKey,
    resolveUserId: () => '00000000-0000-4000-8000-000000000001' as never,
    resolveAttachments: () => attachments,
    resolveFiles: () => new DeepSeekFileStore(),
  })

  const userText = `${decision}\n\n${contextJson}`
  const message = createUserMessage({
    content: [
      { type: 'text', text: userText },
      ...refs.map((attachment) => ({ type: 'image', attachment } as const)),
    ],
    source: { kind: 'plugin', plugin: 'kline-playbook-engine' },
  })

  let rawResponseText = ''
  let finishKind = 'unknown'
  let providerRequestId: string | null = null
  let usage: Record<string, number> = {}
  let error: string | null = null

  try {
    const stream = adapter.stream({
      provider,
      model,
      system,
      messages: [message],
    })
    for await (const chunk of stream) {
      if (chunk.type === 'text-delta') rawResponseText += chunk.text
      else if (chunk.type === 'usage') usage = usageOf(chunk.usage)
      else if (chunk.type === 'finish') {
        finishKind = chunk.reason?.kind ?? 'unknown'
        providerRequestId = extractRequestId(chunk.replayState)
      }
    }
  } catch (cause) {
    error = cause instanceof Error ? cause.message : String(cause)
  }

  const result = {
    status: error ? 'ERROR' : 'OK',
    error,
    provider,
    model,
    request_count: 1,
    image_count: refs.length,
    raw_response_text: rawResponseText,
    finish_reason: finishKind,
    provider_request_id: providerRequestId,
    token_usage: usage,
    harness_admission: {
      provider,
      model,
      images_attached: refs.length,
      retries: 0,
      hidden_second_request: false,
    },
  }
  writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf8')
  return error ? 1 : 0
}

function usageOf(usage: { inputTokens?: number; outputTokens?: number; cacheReadTokens?: number; cacheWriteTokens?: number; reasoningTokens?: number }): Record<string, number> {
  return {
    inputTokens: usage.inputTokens ?? 0,
    outputTokens: usage.outputTokens ?? 0,
    cacheReadTokens: usage.cacheReadTokens ?? 0,
    cacheWriteTokens: usage.cacheWriteTokens ?? 0,
    reasoningTokens: usage.reasoningTokens ?? 0,
  }
}

function extractRequestId(replayState: unknown): string | null {
  if (replayState && typeof replayState === 'object') {
    const response = (replayState as { response?: unknown }).response
    if (response && typeof response === 'object') {
      const id = (response as { id?: unknown }).id
      if (typeof id === 'string' && id.length > 0) return id
    }
  }
  return null
}

main()
  .then((code) => process.exitCode = code)
  .catch((cause) => {
    const message = cause instanceof Error ? cause.message : String(cause)
    writeFileSync(process.argv[process.argv.indexOf('--out') + 1] ?? 'smoke_bridge_error.json',
      JSON.stringify({ status: 'ERROR', error: message }, null, 2), 'utf8')
    process.exitCode = 2
  })
