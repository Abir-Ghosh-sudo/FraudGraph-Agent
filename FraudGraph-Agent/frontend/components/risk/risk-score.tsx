import { cn } from "@/lib/utils";
import { RiskBadge } from "@/components/common/badge";
import { Card } from "@/components/common/card";

export interface RiskScoreProps {
  score: number | null | undefined;
  level?: string | null;
  title?: string;
  description?: string | null;
  showPercentage?: boolean;
  compact?: boolean;
  className?: string;
}

function normalizeScore(
  score: number | null | undefined,
): number | null {
  if (
    score === null ||
    score === undefined ||
    !Number.isFinite(score)
  ) {
    return null;
  }

  return Math.min(
    1,
    Math.max(0, score),
  );
}

function formatScore(
  score: number | null,
  showPercentage: boolean,
): string {
  if (score === null) {
    return "—";
  }

  if (showPercentage) {
    return `${Math.round(score * 100)}%`;
  }

  return score.toFixed(2);
}

function getRiskClass(
  level: string | null | undefined,
): string {
  switch (level?.toLowerCase()) {
    case "critical":
      return "bg-[var(--red)]";

    case "high":
      return "bg-[var(--orange)]";

    case "medium":
      return "bg-[var(--yellow)]";

    case "low":
      return "bg-[var(--lime)]";

    default:
      return "bg-[var(--cyan)]";
  }
}

export function RiskScore({
  score,
  level,
  title = "Risk Score",
  description,
  showPercentage = true,
  compact = false,
  className,
}: RiskScoreProps) {
  const normalizedScore =
    normalizeScore(score);

  const displayScore = formatScore(
    normalizedScore,
    showPercentage,
  );

  const riskLevel =
    level?.trim() || "unknown";

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
          "flex items-start justify-between gap-4",
          compact ? "mb-3" : "mb-5",
        )}
      >
        <div>
          <p className="text-xs font-black uppercase tracking-[0.14em]">
            {title}
          </p>

          {description && (
            <p className="mt-1 text-sm font-bold opacity-70">
              {description}
            </p>
          )}
        </div>

        <RiskBadge
          riskLevel={riskLevel}
          size={compact ? "sm" : "md"}
        />
      </div>

      <div
        className={cn(
          "flex items-end justify-between gap-4",
          compact ? "mb-3" : "mb-4",
        )}
      >
        <span
          className={cn(
            "font-black leading-none tracking-[-0.06em]",
            compact
              ? "text-4xl"
              : "text-5xl sm:text-6xl",
          )}
        >
          {displayScore}
        </span>

        {normalizedScore !== null && (
          <span className="pb-1 text-xs font-black uppercase opacity-60">
            normalized
          </span>
        )}
      </div>

      <div
        className="h-6 border-[3px] border-black bg-white"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={
          normalizedScore === null
            ? undefined
            : Math.round(
                normalizedScore * 100,
              )
        }
        aria-label={`${title}: ${displayScore}`}
      >
        {normalizedScore !== null && (
          <div
            className={cn(
              "h-full border-r-[3px] border-black transition-[width] duration-500",
              getRiskClass(riskLevel),
            )}
            style={{
              width: `${normalizedScore * 100}%`,
            }}
          />
        )}
      </div>

      {normalizedScore === null && (
        <p className="mt-3 text-xs font-black uppercase opacity-60">
          Risk score unavailable
        </p>
      )}
    </Card>
  );
}

export default RiskScore;
