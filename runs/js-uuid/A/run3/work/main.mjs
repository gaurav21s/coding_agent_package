import { v4 as uuidv4, v7 as uuidv7, validate, version } from 'uuid';

/**
 * Generates and validates UUIDs of version 4 and 7.
 */
function run() {
    // Generate UUIDs
    const idV4 = uuidv4();
    const idV7 = uuidv7();

    const uuids = [
        { id: idV4, expectedVersion: 4 },
        { id: idV7, expectedVersion: 7 }
    ];

    uuids.forEach(({ id, expectedVersion }) => {
        // Validate format
        const isValid = validate(id);
        
        // Detect version
        const detectedVersion = version(id);

        console.log(`UUID: ${id}`);
        console.log(`- Valid: ${isValid}`);
        console.log(`- Detected Version: ${detectedVersion}`);
        console.log(`- Matches Expected Version (${expectedVersion}): ${detectedVersion === expectedVersion}`);
        console.log('---');
    });
}

run();
