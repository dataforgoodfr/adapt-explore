import { defineRelations } from "drizzle-orm";
import * as schema from "./schema";

export const relations = defineRelations(schema, (r) => ({
  aleas: {
    localisations: r.many.localisations({
      from: r.aleas.id.through(r.initiatives.aleaId),
      to: r.localisations.id.through(r.initiatives.localisation),
    }),
    initiatives: r.many.initiatives(),
  },
  localisations: {
    aleas: r.many.aleas(),
    initiatives: r.many.initiatives(),
  },
  initiatives: {
    alea: r.one.aleas({
      from: r.initiatives.aleaId,
      to: r.aleas.id,
    }),
    localisationRelation: r.one.localisations({
      from: r.initiatives.localisation,
      to: r.localisations.id,
    }),
  },
  tasksJobs: {
    task: r.one.tasks({
      from: r.tasksJobs.taskId,
      to: r.tasks.id,
    }),
    tasksJobsSummaries: r.one.tasksJobsSummaries(),
  },
  tasks: {
    tasksJobs: r.many.tasksJobs(),
  },
  tasksJobsSummaries: {
    tasksJob: r.one.tasksJobs({
      from: r.tasksJobsSummaries.jobId,
      to: r.tasksJobs.id,
    }),
  },
}));
