import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type { EvidenceSource as EvidenceSourceRecord } from "@/types/evidence";

export interface EvidenceSourceProps {
  source: EvidenceSourceRecord | null | undefined;
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

export function EvidenceSourceCard({
  source,
  title = "Evidence Source",
  compact = false,
  className,
}: EvidenceSourceProps) {
  if (!source) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <p className="text-sm font-black uppercase opacity-60">
          Source information unavailable
        </p>
      </Card>
    );
  }

  return (
    <Card
      variant="cyan"
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
        <div className="min-w-0">
          <p className="text-[10px] font-black uppercase tracking-[0.14em]">
            {title}
          </p>

          <h3 className="mt-1 break-words text-lg font-black uppercase leading-tight">
            {source.name}
          </h3>

          <p className="mt-1 break-all font-mono text-xs font-bold opacity-60">
            {source.source_id}
          </p>
        </div>

        <Badge
          variant="dark"
          size={compact ? "sm" : "md"}
        >
          {source.source_type}
        </Badge>
      </div>

      {source.description && (
        <p className="mb-4 text-sm font-bold leading-relaxed">
          {source.description}
        </p>
      )}

      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="border-[2px] border-black bg-white p-3">
          <dt className="text-[10px] font-black uppercase opacity-60">
            Provider
          </dt>

          <dd className="mt-1 break-words text-sm font-black">
            {source.provider || "—"}
          </dd>
        </div>

        <div className="border-[2px] border-black bg-white p-3">
          <dt className="text-[10px] font-black uppercase opacity-60">
            Retrieved
          </dt>

          <dd className="mt-1 text-sm font-black">
            {formatDate(
              source.retrieved_at,
            )}
          </dd>
        </div>
      </dl>

      {source.uri && (
        <div className="mt-4 border-[3px] border-black bg-[var(--yellow)] p-3">
          <span className="block text-[10px] font-black uppercase">
            Source URI
          </span>

          <a
            href={source.uri}
            target="_blank"
            rel="noreferrer"
            className="mt-1 block break-all font-mono text-xs font-black underline decoration-[2px] underline-offset-2"
          >
            {source.uri}
          </a>
        </div>
      )}

      {Object.keys(
        source.metadata,
      ).length > 0 && (
        <details className="mt-4 border-[3px] border-black bg-white">
          <summary className="cursor-pointer select-none px-3 py-3 text-xs font-black uppercase">
            Source metadata
          </summary>

          <div className="border-t-[3px] border-black p-3">
            <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-xs font-bold leading-relaxed">
              {JSON.stringify(
                source.metadata,
                null,
                2,
              )}
            </pre>
          </div>
        </details>
      )}
    </Card>
  );
}

export const EvidenceSource =
  EvidenceSourceCard;

export default EvidenceSourceCard;
