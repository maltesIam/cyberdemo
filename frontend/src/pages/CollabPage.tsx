import { CollabChat } from "../components/Collab";

export function CollabPage() {
  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-white">Team Collaboration</h1>
        <p className="text-gray-400 mt-1">Real-time communication for SOC team incident response</p>
      </div>

      <div className="flex-1 min-h-0">
        <CollabChat />
      </div>
    </div>
  );
}
