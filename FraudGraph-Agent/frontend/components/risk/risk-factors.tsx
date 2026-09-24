import { cn } from "@/lib/utils";

import { Card } from "@/components/common/card";
import { Badge } from "@/components/common/badge";

export interface RiskFactor {
  id: string;
  title: string;
  description?: string | null;
  severity?: string | null;
  score?: number | null;
  confidence?: number | null;
  evidenceIds?: string[];
}

export interface RiskFactorsProps {
  factors: RiskFactor[];
  title?: string;
  description?: string | null;
  emptyMessage?: string;
  className?: string;
}

function severityVariant(
  severity: string | null | undefined,
): "default" | "yellow" | "lime" | "pink" | "cyan" | "orange" | "red" | "green" | "dark" | "outline" {
  switch (severity?.toLowerCase()) {
    case "critical":
      return "red";
    case "high":
      return "orange";
    case "medium":
      return "yellow";
    case "low":
      return "lime";
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

export function RiskFactors({
  factors,
  title = "Risk Factors",
  description,
  emptyMessage = "No risk factors were returned by the analysis.",
  className,
}: RiskFactorsProps) {
  return (
    <Card
      variant="orange"
      className={cn(className)}
    >
      <div className="mb-5">
        <div className="flex items-center justify-between gap-3">
          <h2 className="neo-section-title">
            {title}
          </h2>

          <Badge variant="dark" size="sm">
            {factors.length}{" "}
            {factors.length === 1
              ? "factor"
              : "factors"}
          </Badge>
        </div>

        {description && (
          <p className="mt-2 text-sm font-bold opacity-70">
            {description}
          </p>
        )}
      </div>

      {factors.length === 0 ? (
        <div className="neo-empty border-[3px] border-dashed border-black bg-white p-5">
          <p className="text-sm font-black uppercase">
            {emptyMessage}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {factors.map((factor) => (
            <article
              key={factor.id}
              className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]"
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-base font-black uppercase leading-tight">
                      {factor.title}
                    </h3>

                    {factor.severity && (
                      <Badge
                        variant={severityVariant(
                          factor.severity,
                        )}
                        size="sm"
                      >
                        {factor.severity}
                      </Badge>
                    )}
                  </div>

                  {factor.description && (
                    <p className="mt-2 text-sm font-bold leading-relaxed opacity-75">
                      {factor.description}
                    </p>
                  )}
                </div>

                <div className="shrink-0 border-[2px] border-black bg-[var(--cyan)] px-3 py-2 text-center">
                  <span className="block text-[10px] font-black uppercase">
                    Confidence
                  </span>

                  <span className="text-lg font-black">
                    {formatPercentage(
                      factor.confidence,
                    )}
                  </span>
                </div>
              </div>

              {(factor.score !== null &&
                factor.score !== undefined) && (
                <div className="mt-4">
                  <div className="mb-1 flex items-center justify-between gap-3">
                    <span className="text-xs font-black uppercase">
                      Factor score
                    </span>

                    <span className="text-xs font-black">
                      {formatPercentage(
                        factor.score,
                      )}
                    </span>
                  </div>

                  <div
                    className="h-4 border-[2px] border-black bg-[var(--bg)]"
                    role="progressbar"
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-valuenow={
                      Number.isFinite(
                        factor.score,
                      )
                        ? Math.round(
                            Math.min(
                              100,
                              Math.max(
                                0,
                                factor.score > 1
                                  ? factor.score
                                  : factor.score *
                                      100,
                              ),
                            ),
                          )
                        : undefined
                    }
                    aria-label={`${factor.title} score`}
                  >
                    <div
                      className="h-full bg-[var(--red)]"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            (factor.score > 1
                              ? factor.score
                              : factor.score * 100),
                          ),
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {factor.evidenceIds &&
                factor.evidenceIds.length > 0 && (
                  <div className="mt-4 flex flex-wrap items-center gap-2 border-t-[2px] border-black pt-3">
                    <span className="text-xs font-black uppercase">
                      Evidence
                    </span>

                    {factor.evidenceIds.map(
                      (evidenceId) => (
                        <span
                          key={evidenceId}
                          className="border-[2px] border-black bg-[var(--lime)] px-2 py-1 font-mono text-[11px] font-black"
                        >
                          {evidenceId}
                        </span>
                      ),
                    )}
                  </div>
                )}
            </article>
          ))}
        </div>
      )}
    </Card>
  );
}

export default RiskFactors;