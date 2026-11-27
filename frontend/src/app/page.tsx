import { Suspense } from "react";
import InitiativesByTypes from "./components/initiatives-by-types";

export default async function Home() {
  return (
    <div>
      <Suspense fallback="{<div>...</div>}">
        <div className="grid grid-cols-3 gap-4 mx-4">
          <InitiativesByTypes />
        </div>
      </Suspense>
    </div>
  );
}
