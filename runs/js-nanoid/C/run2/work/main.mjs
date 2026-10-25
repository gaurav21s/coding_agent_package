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
