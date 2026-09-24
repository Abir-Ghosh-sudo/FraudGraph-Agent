import { cn } from "@/lib/utils";

import {
  EmptyState,
  Loading,
  ErrorState,
} from "@/components/common/loading";
import { EvidenceCard } from "@/components/evidence/evidence-card";
import type { Evidence } from "@/types/evidence";

export interface EvidenceListProps {
  evidence: Evidence[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void | Promise<void>;
  onEvidenceClick?: (
    evidence: Evidence,
  ) => void;
  title?: string;
  description?: string | null;
  emptyTitle?: string;
  emptyMessage?: string;
  compact?: boolean;
  className?: string;
}

export function EvidenceList({
  evidence,
  loading = false,
  error = null,
  onRetry,
  onEvidenceClick,
  title = "Evidence",
  description,
  emptyTitle = "No evidence found",
  emptyMessage = "No evidence has been returned for this investigation.",
  compact = false,
  className,
}: EvidenceListProps) {
  if (loading) {
    return (
      <div
        className={cn(
          "border-[3px] border-black bg-white p-5 shadow-[5px_5px_0_#000]",
          className,
        )}
      >
        <Loading label="Loading evidence..." />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={onRetry}
        className={className}
      />
    );
  }

  return (
    <section className={className}>
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="neo-section-title">
            {title}
          </h2>

          {description && (
            <p className="mt-1 text-sm font-bold opacity-70">
              {description}
            </p>
          )}
        </div>

        <div className="w-fit border-[3px] border-black bg-[var(--cyan)] px-3 py-2 text-xs font-black uppercase shadow-[3px_3px_0_#000]">
          {evidence.length}{" "}
          {evidence.length === 1
            ? "item"
            : "items"}
        </div>
      </div>

      {evidence.length === 0 ? (
        <EmptyState
          title={emptyTitle}
          message={emptyMessage}
        />
      ) : (
        <div
          className={cn(
            "grid gap-5",
            compact
              ? "grid-cols-1"
              : "grid-cols-1 xl:grid-cols-2",
          )}
        >
          {evidence.map((item) => (
            <EvidenceCard
              key={item.evidence_id}
              evidence={item}
              compact={compact}
              onClick={onEvidenceClick}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default EvidenceList;