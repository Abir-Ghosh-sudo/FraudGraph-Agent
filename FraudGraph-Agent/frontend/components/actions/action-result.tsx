import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type { ActionResult as ActionExecutionResult } from "@/types/action";

export interface ActionResultProps {
  result: ActionExecutionResult | null | undefined;
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

export function ActionResultCard({
  result,
  title = "Action Result",
  compact = false,
  className,
}: ActionResultProps) {
  if (!result) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <p className="text-sm font-black uppercase opacity-60">
          No execution result available
        </p>
      </Card>
    );
  }

  const dataKeys = Object.keys(
    result.data,
  );

  return (
    <Card
      variant={result.success ? "lime" : "red"}
      className={cn(
        compact && "p-4",
        className,
      )}
    >
      <div
        className={cn(
          "flex items-start justify-between gap-4",
          compact ? "mb-4" : "mb-5",
        )}
      >
        <div>
          <p className="text-[10px] font-black uppercase tracking-[0.14em]">
            {title}
          </p>

          <h2 className="mt-1 text-xl font-black uppercase">
            {result.success
              ? "Execution completed"
              : "Execution failed"}
          </h2>
        </div>

        <Badge
          variant={
            result.success
              ? "green"
              : "red"
          }
          size="md"
        >
          {result.status}
        </Badge>
      </div>

      {result.message && (
        <div className="border-[3px] border-black bg-white p-4">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Message
          </span>

          <p className="mt-1 text-sm font-bold leading-relaxed">
            {result.message}
          </p>
        </div>
      )}

      {result.error && (
        <div className="mt-4 border-[3px] border-black bg-[var(--red)] p-4">
          <span className="block text-[10px] font-black uppercase">
            Error
          </span>

          <p className="mt-1 break-words text-sm font-black leading-relaxed">
            {result.error}
          </p>
        </div>
      )}

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Status
          </span>

          <span className="mt-1 block text-sm font-black uppercase">
            {result.status}
          </span>
        </div>

        <div className="border-[2px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Executed
          </span>

          <span className="mt-1 block text-sm font-black">
            {formatDate(
              result.executed_at,
            )}
          </span>
        </div>
      </div>

      {dataKeys.length > 0 && (
        <div className="mt-4 border-[3px] border-black bg-white">
          <div className="border-b-[3px] border-black bg-[var(--yellow)] px-4 py-3">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-xs font-black uppercase">
                Returned data
              </h3>

              <Badge
                variant="dark"
                size="sm"
              >
                {dataKeys.length} fields
              </Badge>
            </div>
          </div>

          <div className="overflow-x-auto p-4">
            <dl className="space-y-3">
              {dataKeys.map((key) => (
                <div
                  key={key}
                  className="grid gap-1 border-b-[2px] border-black pb-3 last:border-b-0 last:pb-0 sm:grid-cols-[minmax(140px,0.35fr)_1fr]"
                >
                  <dt className="break-words text-xs font-black uppercase opacity-60">
                    {key}
                  </dt>

                  <dd className="break-words font-mono text-xs font-bold">
                    {formatValue(
                      result.data[key],
                    )}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}

      {dataKeys.length === 0 && (
        <div className="mt-4 border-[2px] border-dashed border-black p-3">
          <p className="text-xs font-black uppercase opacity-60">
            No additional result data returned
          </p>
        </div>
      )}
    </Card>
  );
}

function formatValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export const ActionResult =
  ActionResultCard;

export default ActionResultCard;
