To address your requirements, I have reviewed the `nanoid` library documentation and changelog. As noted in your provided changelog, the `nanoid` library removed its `async` API in version 4.0.0 because the underlying Web Crypto API (which `nanoid` uses for secure random generation) is synchronous in the context of the environment where `nanoid` operates.

Therefore, the following program uses the current `nanoid` (v5.0.9) synchronous API, which is the standard and recommended way to generate IDs in modern Node.js environments.

```javascript
import { nanoid, customAlphabet } from 'nanoid';

/**
 * Program: main.mjs
 * Description: Generates IDs using nanoid v5.0.9.
 * Note: As per nanoid v4+ changelog, the async API has been removed 
 * as the underlying Web Crypto API is synchronous.
 */

async function run() {
    // 1. Default-length ID (21 characters)
    const defaultId = nanoid();

    // 2. 10-character ID
    const tenCharId = nanoid(10);

    // 3. 6-character ID made only of digits
    const digits = '0123456789';
    const nanoidDigits = customAlphabet(digits, 6);
    const customId = nanoidDigits();

    // Output results
    const results = [
        { label: 'Default-length ID', id: defaultId },
        { label: '10-character ID', id: tenCharId },
        { label: '6-character digit ID', id: customId }
    ];

    results.forEach(item => {
        console.log(`${item.label}: ${item.id} (Length: ${item.id.length})`);
    });
}

run().catch(err => console.error(err));
```