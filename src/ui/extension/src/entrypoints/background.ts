import { defineBackground } from 'wxt/utils/define-background';

export default defineBackground(() => {
  // Empty shell (AST-1254): no network, no messaging, no capture.
  // AST-1255 / AST-1256 own session + icon-click paths on this background context.
});
