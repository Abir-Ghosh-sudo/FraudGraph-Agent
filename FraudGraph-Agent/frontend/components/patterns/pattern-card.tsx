import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";

export interface PatternEvidence {
  evidence_id?: string;
  title?: string;
  description?: string | null;
  confidence?: number | null;
}

export interface Pattern {
  pattern_id: string;
  name: string;
  description?: string | null;
  type?: string | null;
  confidence?: number | null;
  risk_score?: number | null;
  fraud_probability?: number | null;
  evidence?: PatternEvidence[];
  evidence_ids?: string[];
  metadata?: Record<string, unknown>;
}

export interface PatternCardProps {
  pattern: Pattern;
  compact?: boolean;
  onClick?: (pattern: Pattern) => void;
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

function getRiskVariant(
  score: number | null | undefined,
): "lime" | "yellow" | "orange" | "red" | "outline" {
  if (
    score === null ||
    score === undefined ||
    !Number.isFinite(score)
  ) {
    return "outline";
  }

  const normalized =
    score > 1 ? score / 100 : score;

  if (normalized >= 0.8) {
    return "red";
  }

  if (normalized >= 0.6) {
    return "orange";
  }

  if (normalized >= 0.4) {
    return "yellow";
  }

  return "lime";
}

export function PatternCard({
  pattern,
  compact = false,
  onClick,
  className,
}: PatternCardProps) {
  const interactive = Boolean(onClick);

  const riskValue =
    pattern.risk_score ??
    pattern.fraud_probability ??
    null;

  return (
    <Card
      variant="pink"
      className={cn(
        interactive &&
          "cursor-pointer transition-none hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[7px_7px_0_#000]",
        compact && "p-4",
        className,
      )}
      onClick={
        onClick
          ? () => onClick(pattern)
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
                onClick?.(pattern);
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
            {pattern.type && (
              <Badge
                variant="dark"
                size="sm"
              >
                {pattern.type}
              </Badge>
            )}

            <span className="font-mono text-[11px] font-black opacity-60">
              {pattern.pattern_id}
            </span>
          </div>

          <h3 className="text-lg font-black uppercase leading-tight">
            {pattern.name}
          </h3>
        </div>

        {pattern.confidence !==
          null &&
          pattern.confidence !==
            undefined && (
            <div className="shrink-0 border-[2px] border-black bg-[var(--cyan)] px-3 py-2 text-center">
              <span className="block text-[9px] font-black uppercase">
                Confidence
              </span>

              <span className="text-lg font-black">
                {formatPercentage(
                  pattern.confidence,
                )}
              </span>
            </div>
          )}
      </div>

      {pattern.description && (
        <p className="mb-4 text-sm font-bold leading-relaxed">
          {pattern.description}
        </p>
      )}

      {(pattern.risk_score !==
        null &&
        pattern.risk_score !==
          undefined) ||
      (pattern.fraud_probability !==
        null &&
        pattern.fraud_probability !==
          undefined) ? (
        <div className="mb-4 border-[3px] border-black bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs font-black uppercase">
              {pattern.fraud_probability !==
              null &&
              pattern.fraud_probability !==
                undefined
                ? "Fraud probability"
                : "Risk score"}
            </span>

            <Badge
              variant={getRiskVariant(
                riskValue,
              )}
              size="sm"
            >
              {formatPercentage(
                riskValue,
              )}
            </Badge>
          </div>

          <div className="mt-3 h-4 border-[2px] border-black bg-[var(--bg)]">
            <div
              className={cn(
                "h-full",
                getRiskVariant(
                  riskValue,
                ) === "red" &&
                  "bg-[var(--red)]",
                getRiskVariant(
                  riskValue,
                ) === "orange" &&
                  "bg-[var(--orange)]",
                getRiskVariant(
                  riskValue,
                ) === "yellow" &&
                  "bg-[var(--yellow)]",
                getRiskVariant(
                  riskValue,
                ) === "lime" &&
                  "bg-[var(--lime)]",
              )}
              style={{
                width: `${Math.min(
                  100,
                  Math.max(
                    0,
                    riskValue! > 1
                      ? riskValue!
                      : riskValue! * 100,
                  ),
                )}%`,
              }}
            />
          </div>
        </div>
      ) : null}

      {pattern.evidence &&
        pattern.evidence.length > 0 && (
          <div className="border-t-[3px] border-black pt-4">
            <div className="mb-3 flex items-center justify-between gap-3">
              <h4 className="text-xs font-black uppercase tracking-[0.12em]">
                Supporting evidence
              </h4>

              <Badge
                variant="yellow"
                size="sm"
              >
                {pattern.evidence.length}
              </Badge>
            </div>

            <div className="space-y-2">
              {pattern.evidence.map(
                (item, index) => (
                  <div
                    key={
                      item.evidence_id ??
                      `${pattern.pattern_id}-evidence-${index}`
                    }
                    className="border-[2px] border-black bg-white p-3"
                  >
                    {item.title && (
                      <p className="text-sm font-black">
                        {item.title}
                      </p>
                    )}

                    {item.description && (
                      <p className="mt-1 text-xs font-bold leading-relaxed opacity-70">
                        {item.description}
                      </p>
                    )}

                    {item.confidence !==
                      null &&
                      item.confidence !==
                        undefined && (
                        <p className="mt-2 text-[10px] font-black uppercase">
                          Confidence:{" "}
                          {formatPercentage(
                            item.confidence,
                          )}
                        </p>
                      )}
                  </div>
                ),
              )}
            </div>
          </div>
        )}

      {(!pattern.evidence ||
        pattern.evidence.length === 0) &&
        pattern.evidence_ids &&
        pattern.evidence_ids.length >
          0 && (
          <div className="border-t-[3px] border-black pt-4">
            <h4 className="mb-3 text-xs font-black uppercase tracking-[0.12em]">
              Evidence IDs
            </h4>

            <div className="flex flex-wrap gap-2">
              {pattern.evidence_ids.map(
                (evidenceId) => (
                  <span
                    key={evidenceId}
                    className="border-[2px] border-black bg-white px-2 py-1 font-mono text-[11px] font-black"
                  >
                    {evidenceId}
                  </span>
                ),
              )}
            </div>
          </div>
        )}
    </Card>
  );
}

export default PatternCard;