import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type { CaseFinding } from "@/types/case";

export interface FindingsProps {
  findings: CaseFinding[];
  title?: string;
  description?: string;
  compact?: boolean;
  onEvidenceClick?: (
    evidenceId: string,
  ) => void;
  className?: string;
}

function formatConfidence(
  value: number | null,
): string {
  if (
    value === null ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  const percentage =
    value <= 1 ? value * 100 : value;

  return `${Math.round(
    Math.min(100, Math.max(0, percentage)),
  )}%`;
}

function formatDate(
  value: string,
): string {
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

export function Findings({
  findings,
  title = "Findings",
  description = "Evidence-backed findings produced during the investigation.",
  compact = false,
  onEvidenceClick,
  className,
}: FindingsProps) {
  if (findings.length === 0) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">
          {title}
        </span>

        <p className="mt-1 text-sm font-black uppercase">
          No findings available
        </p>

        <p className="mt-1 text-xs font-bold opacity-60">
          {description}
        </p>
      </Card>
    );
  }

  return (
    <section
      className={cn(
        "border-[3px] border-black bg-[var(--surface)] p-5 shadow-[6px_6px_0_#000]",
        compact && "p-4",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">
            Case analysis
          </span>

          <h2 className="mt-1 text-xl font-black uppercase">
            {title}
          </h2>

          <p className="mt-1 max-w-2xl text-xs font-bold opacity-70">
            {description}
          </p>
        </div>

        <Badge
          variant="pink"
          size="sm"
        >
          {findings.length}{" "}
          {findings.length === 1
            ? "finding"
            : "findings"}
        </Badge>
      </div>

      <div className="mt-5 space-y-4">
        {findings.map((finding) => (
          <FindingCard
            key={finding.finding_id}
            finding={finding}
            onEvidenceClick={
              onEvidenceClick
            }
          />
        ))}
      </div>
    </section>
  );
}

interface FindingCardProps {
  finding: CaseFinding;
  onEvidenceClick?: (
    evidenceId: string,
  ) => void;
}

function FindingCard({
  finding,
  onEvidenceClick,
}: FindingCardProps) {
  return (
    <article className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="dark"
              size="sm"
            >
              Finding
            </Badge>

            {finding.confidence !==
              null && (
              <Badge
                variant={
                  finding.confidence >=
                  0.8
                    ? "green"
                    : finding.confidence >=
                        0.5
                      ? "yellow"
                      : "orange"
                }
                size="sm"
              >
                {formatConfidence(
                  finding.confidence,
                )}{" "}
                confidence
              </Badge>
            )}
          </div>

          <h3 className="mt-3 text-base font-black uppercase leading-tight">
            {finding.title}
          </h3>

          <p className="mt-1 break-all font-mono text-[9px] font-black opacity-50">
            {finding.finding_id}
          </p>
        </div>

        <time className="shrink-0 text-[10px] font-black uppercase opacity-50">
          {formatDate(
            finding.created_at,
          )}
        </time>
      </div>

      <p className="mt-4 text-sm font-bold leading-relaxed">
        {finding.description}
      </p>

      <div className="mt-4 border-t-[2px] border-black pt-3">
        <div className="flex items-center justify-between gap-3">
          <span className="text-[9px] font-black uppercase opacity-60">
            Supporting evidence
          </span>

          <span className="text-[9px] font-black uppercase opacity-50">
            {finding.evidence_ids.length}{" "}
            linked
          </span>
        </div>

        {finding.evidence_ids.length >
        0 ? (
          <div className="mt-2 flex flex-wrap gap-2">
            {finding.evidence_ids.map(
              (evidenceId) => {
                const interactive =
                  Boolean(
                    onEvidenceClick,
                  );

                return (
                  <button
                    key={evidenceId}
                    type="button"
                    disabled={!interactive}
                    onClick={() =>
                      onEvidenceClick?.(
                        evidenceId,
                      )
                    }
                    className={cn(
                      "border-[2px] border-black bg-[var(--cyan)] px-2 py-1 font-mono text-[9px] font-black",
                      interactive &&
                        "cursor-pointer hover:bg-[var(--yellow)]",
                      !interactive &&
                        "cursor-default",
                    )}
                  >
                    {evidenceId}
                  </button>
                );
              },
            )}
          </div>
        ) : (
          <p className="mt-2 text-xs font-black uppercase opacity-50">
            No evidence references
          </p>
        )}
      </div>
    </article>
  );
}

export default Findings;