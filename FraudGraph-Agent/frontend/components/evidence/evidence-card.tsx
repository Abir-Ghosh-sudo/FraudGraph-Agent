import { cn } from "@/lib/utils";

import {
  Badge,
  getStatusBadgeVariant,
} from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type {
  Evidence,
  EvidenceStrength,
} from "@/types/evidence";

export interface EvidenceCardProps {
  evidence: Evidence;
  compact?: boolean;
  onClick?: (evidence: Evidence) => void;
  className?: string;
}

function strengthVariant(
  strength: EvidenceStrength | null,
): "default" | "yellow" | "lime" | "pink" | "cyan" | "orange" | "red" | "green" | "dark" | "outline" {
  switch (strength) {
    case "conclusive":
      return "red";
    case "strong":
      return "orange";
    case "moderate":
      return "yellow";
    case "weak":
      return "outline";
    default:
      return "outline";
  }
}

function formatPercentage(
  value: number | null | undefined,
): string {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  const normalized =
    value > 1 ? value : value * 100;

  return `${Math.round(
    Math.min(100, Math.max(0, normalized)),
  )}%`;
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

export function EvidenceCard({
  evidence,
  compact = false,
  onClick,
  className,
}: EvidenceCardProps) {
  const interactive = Boolean(onClick);

  return (
    <Card
      variant="default"
      className={cn(
        "transition-none",
        interactive &&
          "cursor-pointer hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[7px_7px_0_#000]",
        compact && "p-4",
        className,
      )}
      onClick={
        onClick
          ? () => onClick(evidence)
          : undefined
      }
      role={
        interactive ? "button" : undefined
      }
      tabIndex={interactive ? 0 : undefined}
      onKeyDown={
        interactive
          ? (event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                event.preventDefault();
                onClick?.(evidence);
              }
            }
          : undefined
      }
    >
      <div
        className={cn(
          "flex items-start justify-between gap-4",
          compact ? "mb-3" : "mb-4",
        )}
      >
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge
              variant="cyan"
              size="sm"
            >
              {evidence.type}
            </Badge>

            <Badge
              variant={getStatusBadgeVariant(
                evidence.status,
              )}
              size="sm"
            >
              {evidence.status}
            </Badge>

            {evidence.strength && (
              <Badge
                variant={strengthVariant(
                  evidence.strength,
                )}
                size="sm"
              >
                {evidence.strength}
              </Badge>
            )}
          </div>

          <h3 className="text-lg font-black uppercase leading-tight">
            {evidence.title}
          </h3>

          <p className="mt-1 font-mono text-xs font-bold opacity-60">
            {evidence.evidence_id}
          </p>
        </div>

        {evidence.confidence !== null && (
          <div className="shrink-0 border-[2px] border-black bg-[var(--lime)] px-3 py-2 text-center">
            <span className="block text-[9px] font-black uppercase">
              Confidence
            </span>

            <span className="text-lg font-black">
              {formatPercentage(
                evidence.confidence,
              )}
            </span>
          </div>
        )}
      </div>

      {evidence.description && (
        <p className="mb-4 text-sm font-bold leading-relaxed">
          {evidence.description}
        </p>
      )}

      {evidence.content && (
        <div className="mb-4 border-[3px] border-black bg-[var(--bg)] p-3">
          <p className="whitespace-pre-wrap break-words text-sm font-medium leading-relaxed">
            {evidence.content}
          </p>
        </div>
      )}

      <div className="grid gap-3 border-t-[3px] border-black pt-4 sm:grid-cols-2">
        <div>
          <span className="block text-[10px] font-black uppercase opacity-60">
            Relevance
          </span>

          <span className="text-sm font-black">
            {formatPercentage(
              evidence.relevance,
            )}
          </span>
        </div>

        <div>
          <span className="block text-[10px] font-black uppercase opacity-60">
            Created
          </span>

          <span className="text-sm font-black">
            {formatDate(evidence.created_at)}
          </span>
        </div>
      </div>

      {evidence.source && (
        <div className="mt-4 border-[3px] border-black bg-[var(--yellow)] p-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <span className="block text-[10px] font-black uppercase">
                Evidence source
              </span>

              <p className="mt-1 text-sm font-black">
                {evidence.source.name}
              </p>

              {evidence.source.provider && (
                <p className="mt-1 text-xs font-bold opacity-70">
                  Provider:{" "}
                  {evidence.source.provider}
                </p>
              )}
            </div>

            <Badge
              variant="dark"
              size="sm"
            >
              {evidence.source.source_type}
            </Badge>
          </div>

          {evidence.source.description && (
            <p className="mt-2 text-xs font-bold leading-relaxed">
              {evidence.source.description}
            </p>
          )}

          {evidence.source.retrieved_at && (
            <p className="mt-2 text-[11px] font-bold opacity-60">
              Retrieved:{" "}
              {formatDate(
                evidence.source.retrieved_at,
              )}
            </p>
          )}
        </div>
      )}

      {evidence.tags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {evidence.tags.map((tag) => (
            <span
              key={tag}
              className="border-[2px] border-black bg-white px-2 py-1 text-[11px] font-black uppercase"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </Card>
  );
}

export default EvidenceCard;