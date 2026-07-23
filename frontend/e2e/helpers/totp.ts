import { createHmac } from 'node:crypto'

const BASE32_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

function base32Decode(secret: string): Buffer {
  const clean = secret.toUpperCase().replace(/=+$/, '')
  let bits = ''
  for (const char of clean) {
    const index = BASE32_ALPHABET.indexOf(char)
    if (index === -1) throw new Error(`Invalid base32 character: ${char}`)
    bits += index.toString(2).padStart(5, '0')
  }
  const bytes: number[] = []
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    bytes.push(parseInt(bits.slice(i, i + 8), 2))
  }
  return Buffer.from(bytes)
}

/**
 * RFC 6238 TOTP over Node's stdlib `crypto` — no dependency needed for a
 * one-off 6-digit code, matching backend/accounts/totp.py's pyotp defaults
 * (SHA1, 30s step, 6 digits).
 */
export function generateTotpCode(base32Secret: string, forTimeMs = Date.now()): string {
  const key = base32Decode(base32Secret)
  const counter = Math.floor(forTimeMs / 1000 / 30)
  const counterBuffer = Buffer.alloc(8)
  counterBuffer.writeBigUInt64BE(BigInt(counter))

  const hmac = createHmac('sha1', key).update(counterBuffer).digest()
  const offset = hmac[hmac.length - 1] & 0x0f
  const binary =
    ((hmac[offset] & 0x7f) << 24) |
    ((hmac[offset + 1] & 0xff) << 16) |
    ((hmac[offset + 2] & 0xff) << 8) |
    (hmac[offset + 3] & 0xff)
  return String(binary % 1_000_000).padStart(6, '0')
}
