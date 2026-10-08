/** Shared by global-setup, global-teardown and specs. Override the port with E2E_LLM_STUB_PORT. */
export const STUB_PORT = Number(process.env.E2E_LLM_STUB_PORT ?? 8183);
export const STUB_BASE_URL = `http://127.0.0.1:${STUB_PORT}`;
export const STUB_PID_FILE = '/tmp/playwright-llm-stub.pid';
export const STUB_LOG_FILE = '/tmp/playwright-llm-stub.log';
