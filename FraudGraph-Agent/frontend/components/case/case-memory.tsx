import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type { CaseMemoryReference } from "@/types/case";

export interface CaseMemoryProps {
  relatedCases?: CaseMemoryReference[];
  memoryIds?: string[];
  title?: string;
  description?: string;
  compact?: boolean;
  onCaseClick?: (
    caseId: string,
  ) => void;
  className?: string;
}

function formatSimilarity(
  value: number | null | undefined,
): string {
  if (
    value === null ||
    value === undefined ||
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

export function CaseMemory({
  relatedCases = [],
  memoryIds = [],
  title = "Case Memory",
  description = "Related historical cases and retrieved memory references.",
  compact = false,
  onCaseClick,
  className,
}: CaseMemoryProps) {
  const hasRelatedCases =
    relatedCases.length > 0;

  const hasMemoryIds =
    memoryIds.length > 0;

  if (!hasRelatedCases && !hasMemoryIds) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">
            {title}
          </span>

          <p className="mt-1 text-sm font-black uppercase">
            No related memory available
          </p>

          <p className="mt-1 text-xs font-bold opacity-60">
            {description}
          </p>
        </div>
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.14em]">
            {title}
          </span>

          <h3 className="mt-1 text-xl font-black uppercase">
            Historical context
          </h3>

          <p className="mt-1 max-w-2xl text-xs font-bold opacity-70">
            {description}
          </p>
        </div>

        <Badge
          variant="dark"
          size="sm"
        >
          {relatedCases.length +
            memoryIds.length}{" "}
          references
        </Badge>
      </div>

      {hasRelatedCases && (
        <section className="mt-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h4 className="text-xs font-black uppercase">
              Related cases
            </h4>

            <span className="text-[10px] font-black uppercase opacity-60">
              {relatedCases.length} linked
            </span>
          </div>

          <div className="space-y-3">
            {relatedCases.map(
              (relatedCase) => (
                <RelatedCase
                  key={`${relatedCase.memory_id}:${relatedCase.case_id}`}
                  reference={relatedCase}
                  onClick={
                    onCaseClick
                  }
                />
              ),
            )}
          </div>
        </section>
      )}

      {hasMemoryIds && (
        <section
          className={cn(
            "border-t-[3px] border-black pt-4",
            hasRelatedCases && "mt-5",
          )}
        >
          <div className="mb-3 flex items-center justify-between gap-3">
            <h4 className="text-xs font-black uppercase">
              Memory references
            </h4>

            <span className="text-[10px] font-black uppercase opacity-60">
              {memoryIds.length} stored
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            {memoryIds.map(
              (memoryId) => (
                <div
                  key={memoryId}
                  className="border-[2px] border-black bg-white px-3 py-2"
                >
                  <span className="block text-[8px] font-black uppercase opacity-50">
                    Memory ID
                  </span>

                  <span className="break-all font-mono text-[10px] font-black">
                    {memoryId}
                  </span>
                </div>
              ),
            )}
          </div>
        </section>
      )}
    </Card>
  );
}

interface RelatedCaseProps {
  reference: CaseMemoryReference;
  onClick?: (
    caseId: string,
  ) => void;
}

function RelatedCase({
  reference,
  onClick,
}: RelatedCaseProps) {
  const interactive =
    Boolean(onClick);

  return (
    <button
      type="button"
      disabled={!interactive}
      onClick={() =>
        onClick?.(reference.case_id)
      }
      className={cn(
        "w-full border-[3px] border-black bg-white p-4 text-left shadow-[4px_4px_0_#000]",
        interactive &&
          "cursor-pointer transition-none hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0_#000]",
        !interactive &&
          "cursor-default",
      )}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <span className="block text-[9px] font-black uppercase opacity-50">
            Related case
          </span>

          <span className="mt-1 block break-all font-mono text-sm font-black">
            {reference.case_id}
          </span>

          {reference.relevance_reason && (
            <p className="mt-2 text-xs font-bold leading-relaxed">
              {reference.relevance_reason}
            </p>
          )}
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          {reference.similarity !==
            null &&
            reference.similarity !==
              undefined && (
              <Badge
                variant="lime"
                size="sm"
              >
                {formatSimilarity(
                  reference.similarity,
                )}{" "}
                similarity
              </Badge>
            )}

          <Badge
            variant="dark"
            size="sm"
          >
            Memory
          </Badge>
        </div>
      </div>

      <div className="mt-3 border-t-[2px] border-black pt-2">
        <span className="break-all font-mono text-[9px] font-black uppercase opacity-50">
          Memory: {reference.memory_id}
        </span>
      </div>
    </button>
  );
}

export default CaseMemory;