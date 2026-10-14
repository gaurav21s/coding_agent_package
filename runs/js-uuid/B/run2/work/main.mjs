import { v4 as uuidv4, v7 as uuidv7, validate as uuidValidate, version as uuidVersion } from 'uuid';

/**
 * Generates and validates UUIDs, printing their version.
 */
function run() {
  // Generate UUIDs
  const v4Uuid = uuidv4();
  const v7Uuid = uuidv7();

  const uuids = [
    { label: 'Version 4 (Random)', value: v4Uuid },
    { label: 'Version 7 (Time-ordered)', value: v7Uuid }
  ];

  uuids.forEach(({ label, value }) => {
    // Validate the UUID
    const isValid = uuidValidate(value);
    
    if (isValid) {
      // Detect the version
      const detectedVersion = uuidVersion(value);
      console.log(`${label}: ${value} (Detected Version: ${detectedVersion})`);
    } else {
      console.error(`${label}: ${value} is INVALID.`);
    }
  });
}

run();
