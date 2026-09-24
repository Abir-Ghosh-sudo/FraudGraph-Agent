import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type { EvidenceProvenance } from "@/types/evidence";

export interface ProvenanceProps {
  provenance: EvidenceProvenance | null | undefined;
  title?: string;
  compact?: boolean;
  className?: string;
}

function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}

function Metadata({
  metadata,
}: {
  metadata: Record<string, unknown>;
}) {
  if (Object.keys(metadata).length === 0) {
    return null;
  }

  return (
    <details className="mt-4 border-[3px] border-black bg-white">
      <summary className="cursor-pointer select-none px-3 py-3 text-xs font-black uppercase">
        Provenance metadata
      </summary>

      <div className="border-t-[3px] border-black p-3">
        <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-xs font-bold leading-relaxed">
          {JSON.stringify(
            metadata,
            null,
            2,
          )}
        </pre>
      </div>
    </details>
  );
}

export function Provenance({
  provenance,
  title = "Provenance",
  compact = false,
  className,
}: ProvenanceProps) {
  if (!provenance) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <p className="text-sm font-black uppercase opacity-60">
          Provenance information unavailable
        </p>
      </Card>
    );
  }

  return (
    <Card
      variant="lime"
      className={cn(
        compact && "p-4",
        className,
      )}
    >
      <div
        className={cn(
          "flex items-start justify-between gap-4",
          compact ? "mb-3" : "mb-5",
        )}
      >
        <div>
          <p className="text-[10px] font-black uppercase tracking-[0.14em]">
            Evidence chain
          </p>

          <h2 className="mt-1 text-xl font-black uppercase">
            {title}
          </h2>

          <p className="mt-1 break-all font-mono text-xs font-bold opacity-60">
            {provenance.provenance_id}
          </p>
        </div>

        {provenance.source_type && (
          <Badge
            variant="dark"
            size={compact ? "sm" : "md"}
          >
            {provenance.source_type}
          </Badge>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Collection method
          </span>

          <span className="mt-1 block text-sm font-black">
            {provenance.collection_method ||
              "—"}
          </span>
        </div>

        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Processor
          </span>

          <span className="mt-1 block break-words text-sm font-black">
            {provenance.processor || "—"}
          </span>
        </div>

        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Collected
          </span>

          <span className="mt-1 block text-sm font-black">
            {formatDate(
              provenance.collected_at,
            )}
          </span>
        </div>

        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Processed
          </span>

          <span className="mt-1 block text-sm font-black">
            {formatDate(
              provenance.processed_at,
            )}
          </span>
        </div>
      </div>

      {provenance.source_id && (
        <div className="mt-4 border-[3px] border-black bg-[var(--yellow)] p-3">
          <span className="block text-[10px] font-black uppercase">
            Source ID
          </span>

          <span className="mt-1 block break-all font-mono text-xs font-black">
            {provenance.source_id}
          </span>
        </div>
      )}

      {provenance.chain_of_custody.length >
        0 && (
        <div className="mt-5">
          <h3 className="mb-3 text-xs font-black uppercase tracking-[0.14em]">
            Chain of custody
          </h3>

          <ol className="space-y-3">
            {provenance.chain_of_custody.map(
              (entry, index) => (
                <li
                  key={`${entry}-${index}`}
                  className="relative flex items-start gap-3 border-[2px] border-black bg-white p-3"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center border-[2px] border-black bg-[var(--pink)] text-xs font-black">
                    {index + 1}
                  </span>

                  <span className="break-words pt-1 text-sm font-bold leading-relaxed">
                    {entry}
                  </span>
                </li>
              ),
            )}
          </ol>
        </div>
      )}

      <Metadata
        metadata={provenance.metadata}
      />
    </Card>
  );
}

export default Provenance;