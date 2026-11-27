import { drizzle } from "drizzle-orm/node-postgres";
import { reset, seed } from "drizzle-seed";
import * as schema from "@/db/schema";

export const db = {
  client: drizzle(process.env.DATABASE_URL!),
  seed,
  reset,
  schema,
};
