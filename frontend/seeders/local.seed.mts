import { db } from "@/db/client";
import { reset, seed } from "drizzle-seed";
import * as schema from "@/db/schema";
import { parseArgs } from "node:util";
import { exit } from "node:process";

const args = parseArgs({
  options: {
    up: {
      type: "boolean",
      default: false,
    },
    down: {
      type: "boolean",
      default: false,
    },
  },
  strict: true,
});

async function up() {
  console.log("Starting database seeding...");
  try {
    await seed(db, schema);
    console.log("Database seeded successfully");
  } catch (error) {
    console.error("Error seeding database:", error);
    exit(1);
  }
}

async function down() {
  console.log("Starting database reset...");
  try {
    await reset(db, schema);
    console.log("Database reset successfully");
  } catch (error) {
    console.error("Error resetting database:", error);
    exit(1);
  }
}

if (!args.values.down && !args.values.up) {
  console.log(`
Database seeder

Usage:
  npm run db:seed -- --up    Fill the database with seed data
  npm run db:seed -- --down  Truncate all tables

Options:
  --up    Seed the database
  --down  Reset (truncate) the database
`);
  exit(0);
} else if (args.values.up && args.values.down) {
  console.error("Error: Cannot use both --up and --down simultaneously");
  exit(1);
} else if (args.values.up) {
  await up();
  exit(0);
} else if (args.values.down) {
  await down();
  exit(0);
}
