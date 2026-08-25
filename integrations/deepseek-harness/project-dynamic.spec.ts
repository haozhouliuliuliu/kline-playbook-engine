import { afterEach, describe, expect, it } from 'vitest'
import { appendFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { Context } from '@deepseek-ai/cordis'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import { SessionId } from '@deepseek-ai/dsh-session'
import { defineTool } from '@deepseek-ai/dsh-tools'
import * as agentCore from './packages/examples/agent-spine-demo/src/index.ts'
import { MockAdapter, textResponse, toolCallResponse } from './packages/core/agent-loop/tests/mock-adapter.ts'

const roots: string[] = []

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

function requestText(request: { messages: Array<{ content: Array<Record<string, unknown>> }> }): string {
  return request.messages.flatMap(message => message.content)
    .map(block => block.type === 'text' ? String(block.text ?? '') : '')
    .join('\n')
}

async function projectRuntime(memoryPath: string, auditPath: string, adapter: MockAdapter): Promise<Context> {
  const ctx = new Context()
  await ctx.plugin(agentCore, { workspaceContext: false })
  await new Promise(resolve => setTimeout(resolve, 50))
  ctx.llm.registerAdapter(['project-mock'], adapter)

  ctx.systemPrompt.context({
    name: 'jianghe-project-working-memory',
    order: 10,
    text: () => `PROJECT_WORKING_MEMORY\n${readFileSync(memoryPath, 'utf8')}`,
  })

  ctx.tools.register(defineTool({
    name: 'jianghe_kline_snapshot',
    description: 'Read the project-owned causal K-line snapshot for one futures symbol.',
    parameters: {
      symbol: { type: 'string', required: true },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const before = JSON.parse(readFileSync(memoryPath, 'utf8')) as Record<string, unknown>
      const after = {
        ...before,
        last_symbol: args.symbol,
        last_close: 3130,
        watch_region: '3125-3135',
      }
      writeFileSync(memoryPath, JSON.stringify(after), 'utf8')
      appendFileSync(auditPath, JSON.stringify({
        kind: 'memory_mutation',
        source: 'jianghe_kline_snapshot',
        before,
        after,
      }) + '\n', 'utf8')
      return `${args.symbol}|close=3130|source=PROJECT_CAUSAL_FIXTURE`
    },
  }))

  ctx.on('tools/result', (exec, result) => {
    appendFileSync(auditPath, JSON.stringify({
      kind: 'tool_result',
      call_id: String(exec.callId),
      tool: exec.name,
      is_error: result.isError,
    }) + '\n', 'utf8')
  })

  return ctx
}

describe('kline-playbook-engine Harness dynamic admission', () => {
  it('preserves project working memory across runtime restart and audits memory plus tool activity', async () => {
    const root = mkdtempSync(join(tmpdir(), 'kpe-harness-project-probe-'))
    roots.push(root)
    const memoryPath = join(root, 'working-memory.json')
    const auditPath = join(root, 'audit.jsonl')
    writeFileSync(memoryPath, JSON.stringify({
      last_symbol: null,
      last_close: null,
      watch_region: null,
    }), 'utf8')
    writeFileSync(auditPath, '', 'utf8')

    const adapter = new MockAdapter([
      toolCallResponse('call-kline', 'jianghe_kline_snapshot', { symbol: 'SHFE.rb2607' }),
      textResponse('WAIT'),
    ])
    const ctx = await projectRuntime(memoryPath, auditPath, adapter)
    const handle = await ctx.agents.create({
      sessionId: SessionId('kpe-project-dynamic-probe'),
      meta: { cwd: process.cwd() },
      agentOptions: { provider: 'project-mock', model: 'project-model' },
    })

    handle.agent.followup(createUserMessage({
      content: [{ type: 'text', text: 'Evaluate the current project fixture.' }],
      source: { kind: 'user' },
    }))
    await handle.agent.whenIdle()

    expect(adapter.requests).toHaveLength(2)
    expect(adapter.requests[0]?.provider).toBe('project-mock')
    expect(adapter.requests[0]?.model).toBe('project-model')
    expect(requestText(adapter.requests[0] as never)).toContain('"watch_region":null')
    expect(requestText(adapter.requests[1] as never)).toContain('"watch_region":"3125-3135"')

    const eventTypes = handle.agent.session.events.map(event => event.type)
    expect(eventTypes.filter(type => type === 'request/header')).toHaveLength(2)
    expect(eventTypes).toContain('tool/call')
    expect(eventTypes).toContain('tool/result')
    expect(eventTypes).toContain('assistant/message')

    const audit = readFileSync(auditPath, 'utf8').trim().split('\n').map(line => JSON.parse(line))
    expect(audit).toEqual(expect.arrayContaining([
      expect.objectContaining({ kind: 'memory_mutation', source: 'jianghe_kline_snapshot' }),
      expect.objectContaining({ kind: 'tool_result', tool: 'jianghe_kline_snapshot', is_error: false }),
    ]))

    await handle.dispose()
    await ctx.fiber.dispose()

    const restarted = await projectRuntime(memoryPath, auditPath, new MockAdapter([textResponse('unused')]))
    const assembly = await restarted.systemPrompt.assemble()
    const memoryContext = assembly.contexts.find(context => context.name === 'jianghe-project-working-memory')
    expect(memoryContext?.text).toContain('"last_symbol":"SHFE.rb2607"')
    expect(memoryContext?.text).toContain('"watch_region":"3125-3135"')
    expect(restarted.tools.schemas().map(schema => schema.name)).toContain('jianghe_kline_snapshot')
    await restarted.fiber.dispose()
  })
})
