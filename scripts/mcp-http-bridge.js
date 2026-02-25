#!/usr/bin/env node
/**
 * MCP stdio-to-HTTP Bridge (Content-Length framed)
 *
 * This script bridges between stdio-based MCP protocol (Content-Length framed)
 * used by OpenClaw gateway's mcp-bridge plugin and HTTP-based MCP servers.
 *
 * Protocol: Content-Length: <N>\r\n\r\n<JSON>
 *
 * Usage:
 *   node mcp-http-bridge.js [URL]
 *
 * Default URL: http://localhost:8000/mcp/messages
 */

import http from 'http';

const MCP_URL = process.argv[2] || 'http://localhost:8000/mcp/messages';
const parsedUrl = new URL(MCP_URL);

// Log to stderr so it doesn't interfere with MCP protocol on stdout
const debug = (msg) => {
  if (process.env.MCP_BRIDGE_DEBUG) {
    process.stderr.write(`[mcp-bridge] ${msg}\n`);
  }
};

debug(`Starting MCP HTTP bridge to ${MCP_URL}`);
debug(`Protocol: Content-Length framed`);

// Buffer for incoming data
let buffer = '';
let pendingRequests = 0;
let stdinEnded = false;

function checkExit() {
  if (stdinEnded && pendingRequests === 0) {
    debug('All requests completed, exiting');
    process.exit(0);
  }
}

// Process stdin data
process.stdin.setEncoding('utf-8');

process.stdin.on('data', (chunk) => {
  buffer += chunk;
  processBuffer();
});

process.stdin.on('end', () => {
  debug('stdin ended');
  stdinEnded = true;
  checkExit();
});

function processBuffer() {
  while (true) {
    // Look for Content-Length header
    const headerEnd = buffer.indexOf('\r\n\r\n');
    if (headerEnd === -1) {
      debug('No complete header yet, waiting for more data...');
      return;
    }

    // Parse Content-Length
    const header = buffer.substring(0, headerEnd);
    const match = header.match(/Content-Length:\s*(\d+)/i);
    if (!match) {
      debug(`Invalid header: ${header}`);
      buffer = buffer.substring(headerEnd + 4);
      continue;
    }

    const contentLength = parseInt(match[1], 10);
    const bodyStart = headerEnd + 4;
    const bodyEnd = bodyStart + contentLength;

    // Check if we have the full body
    if (buffer.length < bodyEnd) {
      debug(`Waiting for body: have ${buffer.length - bodyStart}, need ${contentLength}`);
      return;
    }

    // Extract the JSON body
    const jsonBody = buffer.substring(bodyStart, bodyEnd);
    buffer = buffer.substring(bodyEnd);

    debug(`Received message: ${jsonBody.substring(0, 200)}`);

    // Parse and forward
    pendingRequests++;
    let request;
    try {
      request = JSON.parse(jsonBody);
    } catch (e) {
      debug(`Error parsing JSON: ${e.message}`);
      pendingRequests--;
      checkExit();
      continue;
    }

    forwardToHttp(request)
      .then(response => {
        sendResponse(response);
      })
      .catch(e => {
        debug(`Error processing message: ${e.message}`);
        sendError(request.id, -32603, `Bridge error: ${e.message}`);
      })
      .finally(() => {
        pendingRequests--;
        checkExit();
      });
  }
}

async function forwardToHttp(jsonRpcMessage) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(jsonRpcMessage);

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 80,
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    debug(`Forwarding request: ${JSON.stringify(jsonRpcMessage).substring(0, 200)}`);

    const req = http.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        debug(`Response status: ${res.statusCode}`);
        debug(`Response data: ${data.substring(0, 200)}`);

        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${data}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', (e) => {
      debug(`Request error: ${e.message}`);
      reject(e);
    });

    req.write(postData);
    req.end();
  });
}

function sendResponse(response) {
  const json = JSON.stringify(response);
  const payload = `Content-Length: ${Buffer.byteLength(json)}\r\n\r\n${json}`;
  process.stdout.write(payload);
  debug(`Sent response: ${json.substring(0, 200)}`);
}

function sendError(id, code, message) {
  sendResponse({
    jsonrpc: '2.0',
    id: id,
    error: {
      code: code,
      message: message
    }
  });
}

// Handle signals gracefully
process.on('SIGTERM', () => {
  debug('Received SIGTERM, exiting');
  process.exit(0);
});

process.on('SIGINT', () => {
  debug('Received SIGINT, exiting');
  process.exit(0);
});

debug('Bridge ready, waiting for MCP messages on stdin...');
