import {
  bigint,
  bigserial,
  boolean,
  foreignKey,
  integer,
  pgTable,
  point,
  primaryKey,
  serial,
  text,
  timestamp,
  unique,
} from "drizzle-orm/pg-core";

export const aleas = pgTable(
  "aleas",
  {
    id: serial().notNull(),
    nom: text().notNull(),
    commentaire: text(),
  },
  (table) => [primaryKey({ columns: [table.id], name: "aleas_pk" })],
);

export const initiatives = pgTable(
  "initiatives",
  {
    id: serial().notNull(),
    titre: text(),
    typeInitiative: text("type_initiative"),
    liens: text(),
    images: text(),
    description: text(),
    aleaId: integer("alea_id"),
    typePorteurInitiative: text("type_porteur_initiative"),
    nomPorteur: text("nom_porteur"),
    localisation: integer(),
  },
  (table) => [
    primaryKey({ columns: [table.id], name: "initiatives_pk" }),
    foreignKey({
      columns: [table.aleaId],
      foreignColumns: [aleas.id],
      name: "initiatives_alea_id_fkey",
    }),
    foreignKey({
      columns: [table.localisation],
      foreignColumns: [localisations.id],
      name: "initiatives_localisation_fkey",
    }),
  ],
);

export const localisations = pgTable(
  "localisations",
  {
    id: serial().notNull(),
    geoPoint: point("geo_point").notNull(),
    ville: text(),
    codePostale: text("code_postale"),
    region: text(),
    departement: text(),
    pays: text(),
  },
  (table) => [primaryKey({ columns: [table.id], name: "localisations_pk" })],
);

export const sources = pgTable(
  "sources",
  {
    id: serial().notNull(),
    nom: text().notNull(),
    type: text(),
  },
  (table) => [primaryKey({ columns: [table.id], name: "sources_pk" })],
);

export const tasks = pgTable(
  "tasks",
  {
    id: serial().notNull(),
    sourceId: integer("source_id").notNull(),
    nom: text().notNull(),
    nextRun: timestamp("next_run"),
    lastRun: timestamp("last_run"),
    locked: boolean(),
  },
  (table) => [
    primaryKey({ columns: [table.id], name: "tasks_pk" }),
    unique("tasks_source_id_key").on(table.sourceId),
  ],
);

export const tasksJobs = pgTable(
  "tasks_jobs",
  {
    id: bigserial({ mode: "number" }).notNull(),
    taskId: integer("task_id").notNull(),
    status: text(),
    jobTimeout: integer("job_timeout"),
    ttl: integer(),
  },
  (table) => [
    primaryKey({ columns: [table.id], name: "tasks_jobs_pk" }),
    foreignKey({
      columns: [table.taskId],
      foreignColumns: [tasks.id],
      name: "tasks_jobs_task_id_fkey",
    }),
  ],
);

export const tasksJobsSummaries = pgTable(
  "tasks_jobs_summaries",
  {
    id: bigserial({ mode: "number" }).notNull(),
    jobId: bigint("job_id", { mode: "number" }).notNull(),
    message: text(),
  },
  (table) => [
    primaryKey({ columns: [table.id], name: "tasks_jobs_summaries_pk" }),
    foreignKey({
      columns: [table.jobId],
      foreignColumns: [tasksJobs.id],
      name: "tasks_jobs_summaries_job_id_fkey",
    }),
    unique("tasks_jobs_summaries_job_id_key").on(table.jobId),
  ],
);
