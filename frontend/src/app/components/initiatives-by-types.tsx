import { InitiativeService } from "@/services/initiative.service";
import ArrowRightIcon from "../icons/arrow-right.icon";

export default async function InitiativesByTypes() {
  const types = await InitiativeService.groupedByTypes();
  return (
    <div>
      <h2 className="uppercase m-2 text-2xl">Par type d'initiative</h2>
      <ul>
        {types.map(({ type, count }) => (
          <li key={type}>
            <div className="flex justify-between p-2 border-b">
              <span>{type}</span>
              <span>
                <span className="mr-3">{count}</span>
                <ArrowRightIcon />
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
