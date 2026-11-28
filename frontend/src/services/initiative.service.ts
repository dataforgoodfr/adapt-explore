import { sql } from "drizzle-orm";
import { cacheLife } from "next/cache";
import { db } from "@/db/client";
import { initiatives } from "@/db/schema";

async function groupedByTypes() {
  "use cache";
  cacheLife("seconds");
  return await db
    .select({ type: initiatives.typeInitiative, count: sql<number>`sum(id)` })
    .from(initiatives)
    .groupBy(initiatives.typeInitiative);
}

export const InitiativeService = {
  groupedByTypes,
};
