import { z } from 'zod';

// 1. Define Signup Schema
// Using Zod 4 top-level validators as per migration guide
const signupSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
  age: z.int().min(13).optional(),
});

// 2. Parse valid and invalid objects
const validData = {
  email: "test@example.com",
  password: "password123",
  age: 25
};

const invalidData = {
  email: "not-an-email",
  password: "short",
  age: 10
};

console.log("--- Valid Parsing ---");
const validResult = signupSchema.safeParse(validData);
console.log("Success:", validResult.success);

console.log("\n--- Invalid Parsing ---");
const invalidResult = signupSchema.safeParse(invalidData);

if (!invalidResult.success) {
  // Print every issue's path and message
  console.log("Individual Issues:");
  invalidResult.error.issues.forEach((issue) => {
    console.log(`Path: ${issue.path.join('.')}, Message: ${issue.message}`);
  });

  // Print errors grouped per field using treeifyError
  console.log("\nGrouped Errors (Treeified):");
  console.log(JSON.stringify(z.treeifyError(invalidResult.error), null, 2));
}

// 3. Admin Schema
// Using object destructuring for extension as .merge is deprecated
const adminSchema = z.object({
  ...signupSchema.shape,
  role: z.string()
});

console.log("\n--- Admin Parsing ---");
const adminData = {
  email: "admin@corp.com",
  password: "securepassword",
  role: "superuser"
};

const adminResult = adminSchema.safeParse(adminData);
console.log("Admin Success:", adminResult.success);
console.log("Admin Data:", adminResult.data);
