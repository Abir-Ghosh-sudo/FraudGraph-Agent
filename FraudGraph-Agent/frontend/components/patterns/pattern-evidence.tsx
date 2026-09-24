import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";

export interface PatternEvidenceItem {
  evidence_id: string;
  title: string;
  description?: string | null;
  type?: string | null;
  confidence?: number | null;
  relevance?: number | null;
  source?: string | null;
  metadata?: Record<string, unknown>;
}

export interface PatternEvidenceProps {
  evidence: PatternEvidenceItem[];
  title?: string;
  description?: string | null;
  emptyMessage?: string;
  compact?: boolean;
  onEvidenceClick?: (
    evidence: PatternEvidenceItem,
  ) => void;
  className?: string;
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

function getConfidenceVariant(
  value: number | null | undefined,
): "lime" | "yellow" | "orange" | "red" | "outline" {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "outline";
  }

  const normalized =
    value > 1 ? value / 100 : value;

  if (normalized >= 0.8) {
    return "lime";
  }

  if (normalized >= 0.6) {
    return "yellow";
  }

  if (normalized >= 0.4) {
    return "orange";
  }

  return "red";
}

export function PatternEvidence({
  evidence,
  title = "Pattern Evidence",
  description,
  emptyMessage = "No supporting evidence was returned for this pattern.",
  compact = false,
  onEvidenceClick,
  className,
}: PatternEvidenceProps) {
  return (
    <Card
      variant="yellow"
      className={cn(
        compact && "p-4",
        className,
      )}
    >
      <div
        className={cn(
          "flex flex-col gap-2",
          compact ? "mb-4" : "mb-5",
        )}
      >
        <div className="flex items-center justify-between gap-3">
          <h2 className="neo-section-title">
            {title}
          </h2>

          <Badge
            variant="dark"
            size="sm"
          >
            {evidence.length}
          </Badge>
        </div>

        {description && (
          <p className="text-sm font-bold leading-relaxed opacity-70">
            {description}
          </p>
        )}
      </div>

      {evidence.length === 0 ? (
        <div className="border-[3px] border-dashed border-black bg-white p-5">
          <p className="text-sm font-black uppercase">
            {emptyMessage}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {evidence.map((item) => {
            const interactive =
              Boolean(onEvidenceClick);

            return (
              <article
                key={item.evidence_id}
                className={cn(
                  "border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]",
                  interactive &&
                    "cursor-pointer hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0_#000]",
                )}
                role={
                  interactive
                    ? "button"
                    : undefined
                }
                tabIndex={
                  interactive
                    ? 0
                    : undefined
                }
                onClick={
                  onEvidenceClick
                    ? () =>
                        onEvidenceClick(
                          item,
                        )
                    : undefined
                }
                onKeyDown={
                  interactive
                    ? (event) => {
                        if (
                          event.key ===
                            "Enter" ||
                          event.key === " "
                        ) {
                          event.preventDefault();

                          onEvidenceClick?.(
                            item,
                          );
                        }
                      }
                    : undefined
                }
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                      {item.type && (
                        <Badge
                          variant="cyan"
                          size="sm"
                        >
                          {item.type}
                        </Badge>
                      )}

                      <span className="break-all font-mono text-[10px] font-black opacity-60">
                        {item.evidence_id}
                      </span>
                    </div>

                    <h3 className="text-base font-black uppercase leading-tight">
                      {item.title}
                    </h3>
                  </div>

                  {item.confidence !==
                    null &&
                    item.confidence !==
                      undefined && (
                      <Badge
                        variant={getConfidenceVariant(
                          item.confidence,
                        )}
                        size="sm"
                      >
                        {formatPercentage(
                          item.confidence,
                        )}
                      </Badge>
                    )}
                </div>

                {item.description && (
                  <p className="mt-3 text-sm font-bold leading-relaxed opacity-75">
                    {item.description}
                  </p>
                )}

                <div className="mt-4 grid gap-2 sm:grid-cols-2">
                  <div className="border-[2px] border-black bg-[var(--bg)] p-2">
                    <span className="block text-[9px] font-black uppercase opacity-60">
                      Confidence
                    </span>

                    <span className="text-sm font-black">
                      {formatPercentage(
                        item.confidence,
                      )}
                    </span>
                  </div>

                  <div className="border-[2px] border-black bg-[var(--bg)] p-2">
                    <span className="block text-[9px] font-black uppercase opacity-60">
                      Relevance
                    </span>

                    <span className="text-sm font-black">
                      {formatPercentage(
                        item.relevance,
                      )}
                    </span>
                  </div>
                </div>

                {item.source && (
                  <div className="mt-3 border-[2px] border-black bg-[var(--lime)] p-2">
                    <span className="text-[9px] font-black uppercase">
                      Source
                    </span>

                    <p className="mt-1 break-words text-xs font-black">
                      {item.source}
                    </p>
                  </div>
                )}

                {item.metadata &&
                  Object.keys(
                    item.metadata,
                  ).length > 0 && (
                    <details className="mt-3 border-[2px] border-black">
                      <summary className="cursor-pointer px-3 py-2 text-[10px] font-black uppercase">
                        Metadata
                      </summary>

                      <pre className="overflow-x-auto whitespace-pre-wrap break-words border-t-[2px] border-black bg-[var(--bg)] p-3 font-mono text-[10px] font-bold">
                        {JSON.stringify(
                          item.metadata,
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  )}
              </article>
            );
          })}
        </div>
      )}
    </Card>
  );
}

export default PatternEvidence;