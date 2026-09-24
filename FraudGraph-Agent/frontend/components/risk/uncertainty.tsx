import { cn } from "@/lib/utils";

import { Card } from "@/components/common/card";
import { Badge } from "@/components/common/badge";

export interface UncertaintyProps {
  confidence: number | null | undefined;
  title?: string;
  description?: string | null;
  factors?: string[];
  className?: string;
}

function normalizeConfidence(
  confidence: number | null | undefined,
): number | null {
  if (
    confidence === null ||
    confidence === undefined ||
    !Number.isFinite(confidence)
  ) {
    return null;
  }

  const value =
    confidence > 1
      ? confidence / 100
      : confidence;

  return Math.min(
    1,
    Math.max(0, value),
  );
}

function getConfidenceVariant(
  confidence: number | null,
): "lime" | "yellow" | "orange" | "red" | "outline" {
  if (confidence === null) {
    return "outline";
  }

  if (confidence >= 0.8) {
    return "lime";
  }

  if (confidence >= 0.6) {
    return "yellow";
  }

  if (confidence >= 0.4) {
    return "orange";
  }

  return "red";
}

function getConfidenceLabel(
  confidence: number | null,
): string {
  if (confidence === null) {
    return "Unavailable";
  }

  if (confidence >= 0.8) {
    return "High confidence";
  }

  if (confidence >= 0.6) {
    return "Moderate confidence";
  }

  if (confidence >= 0.4) {
    return "Limited confidence";
  }

  return "Low confidence";
}

export function Uncertainty({
  confidence,
  title = "Analysis Confidence",
  description,
  factors = [],
  className,
}: UncertaintyProps) {
  const normalized =
    normalizeConfidence(confidence);

  const percentage =
    normalized === null
      ? null
      : Math.round(normalized * 100);

  const variant =
    getConfidenceVariant(normalized);

  return (
    <Card
      variant="cyan"
      className={cn(className)}
    >
      <div className="flex flex-col gap-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="neo-section-title">
              {title}
            </h2>

            {description && (
              <p className="mt-2 text-sm font-bold leading-relaxed opacity-70">
                {description}
              </p>
            )}
          </div>

          <Badge
            variant={variant}
            size="md"
          >
            {getConfidenceLabel(normalized)}
          </Badge>
        </div>

        <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_#000]">
          <div className="flex items-end justify-between gap-4">
            <span className="text-4xl font-black tracking-[-0.05em] sm:text-5xl">
              {percentage === null
                ? "—"
                : `${percentage}%`}
            </span>

            <span className="text-xs font-black uppercase opacity-60">
              confidence
            </span>
          </div>

          <div
            className="mt-4 h-5 border-[3px] border-black bg-[var(--bg)]"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={
              percentage ?? undefined
            }
            aria-label={`${title}: ${
              percentage === null
                ? "unavailable"
                : `${percentage}%`
            }`}
          >
            {percentage !== null && (
              <div
                className={cn(
                  "h-full transition-[width] duration-500",
                  variant === "lime" &&
                    "bg-[var(--lime)]",
                  variant === "yellow" &&
                    "bg-[var(--yellow)]",
                  variant === "orange" &&
                    "bg-[var(--orange)]",
                  variant === "red" &&
                    "bg-[var(--red)]",
                  variant === "outline" &&
                    "bg-[var(--cyan)]",
                )}
                style={{
                  width: `${percentage}%`,
                }}
              />
            )}
          </div>
        </div>

        {factors.length > 0 && (
          <div>
            <h3 className="mb-3 text-xs font-black uppercase tracking-[0.14em]">
              Uncertainty factors
            </h3>

            <ul className="space-y-2">
              {factors.map(
                (factor, index) => (
                  <li
                    key={`${factor}-${index}`}
                    className="flex items-start gap-3 border-[2px] border-black bg-white p-3"
                  >
                    <span
                      aria-hidden="true"
                      className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center border-[2px] border-black bg-[var(--yellow)] text-xs font-black"
                    >
                      !
                    </span>

                    <span className="text-sm font-bold leading-relaxed">
                      {factor}
                    </span>
                  </li>
                ),
              )}
            </ul>
          </div>
        )}

        {normalized === null && (
          <p className="border-[2px] border-black bg-[var(--yellow)] p-3 text-xs font-black uppercase">
            Confidence information is not available
            from the current analysis.
          </p>
        )}
      </div>
    </Card>
  );
}

export default Uncertainty;