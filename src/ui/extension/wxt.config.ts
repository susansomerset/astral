import { defineConfig } from 'wxt';

// Pinned Chrome extension public key (base64) — stable ID across load-unpacked rebuilds.
const CHROME_EXTENSION_KEY =
  'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA03V1gnG5BNIe9NEeB6MtIbXBv7YEetLrjBFd9MS0Ri3gP2/7RbNzl7c2JcMdBo4eMPX+rOGBZwzAvOspZel+oA3fa/n/1WBlLjojNImZonmqn87c1fSvP3wVmoPuTX3K11VubcsS34Ij7UozkPr4T1i00CCCTMrmKMpZ2gquTeJcsVxHDqc80FviU7yw5RFM7RM0/pvYwRooZuiAaiNydEa7QZ+62GmG8F0sE8xzYfGLj2u7sflHhXwJ5OZLVaicmaaqMctk58ia7gT/h9KUOAlzjqZAVrNaTBrOWffs4A9La4nLGpr+5rM+FCj+GVgUQQ78z8x2GnjWbFVVoYZ/5QIDAQAB';

export default defineConfig({
  srcDir: 'src',
  imports: false,
  manifest: {
    name: 'Astral Surfer',
    description: 'Capture job pages you are already viewing into Astral.',
    version: '0.0.0',
    key: CHROME_EXTENSION_KEY,
    browser_specific_settings: {
      gecko: {
        id: 'surfer@astralcareermatch.com',
        strict_min_version: '109.0',
      },
    },
  },
});
