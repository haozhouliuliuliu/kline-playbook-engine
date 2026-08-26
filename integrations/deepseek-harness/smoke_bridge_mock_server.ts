/**
 * Local zero-cost mock-server driver for the V0.1 replay provider-smoke bridge.
 * Replays the same scripted SSE used by the Harness admission tests. It binds
 * only to 127.0.0.1 and is never a real provider; `REAL_DEEPSEEK_PROVIDER_CALLS = 0`.
 *
 * Usage (from the pinned Harness checkout):
 *   tsx tests-kpe-replay-v0-1/smoke_bridge_mock_server.ts
 * Prints `{"url":"http://127.0.0.1:<port>"}` on stdout, then stays up until
 * stdin closes (the Python-side runner or the shell closes it).
 */
import { mockServer, textEvents } from '../packages/llm/llm-deepseek/tests/mock-server.ts'

const server = await mockServer([{ kind: 'sse', events: textEvents }])
process.stdout.write(JSON.stringify({ url: server.url }) + '\n')

process.stdin.resume()
process.stdin.on('data', async () => {
  await server.close()
  process.exit(0)
})
process.stdin.on('end', async () => {
  await server.close()
  process.exit(0)
})
