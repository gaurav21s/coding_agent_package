To comply with the latest version of `nanoid` (v5.x), we must note that the library has removed its `async` API because the underlying Web Crypto API (used for secure random generation) is synchronous in the environment. Therefore, we use the standard synchronous `nanoid` and `customAlphabet` functions.

Per your requirements, here is the `main.mjs` file:

```javascript
import { nanoid, customAlphabet } from 'nanoid';

/**
 * Nano ID v5.x uses synchronous APIs exclusively as per the latest 
 * library design and migration guidelines.
 */

// 1. Default-length ID (21 characters)
const defaultId = nanoid();

// 2. 10-character ID using default alphabet
const tenCharId = nanoid(10);

// 3. 6-character ID made only of digits (0-9)
const digits = '0123456789';
const nanoidDigits = customAlphabet(digits, 6);
const customId = nanoidDigits();

// Output results
console.log(`Default ID: ${defaultId} (Length: ${defaultId.length})`);
console.log(`10-char ID: ${tenCharId} (Length: ${tenCharId.length})`);
console.log(`6-digit ID: ${customId} (Length: ${customId.length})`);
```