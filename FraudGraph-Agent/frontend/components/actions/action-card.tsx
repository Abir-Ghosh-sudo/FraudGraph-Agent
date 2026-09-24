import { cn } from "@/lib/utils";

import {
  Badge,
  getStatusBadgeVariant,
} from "@/components/common/badge";
import { Card } from "@/components/common/card";
import type {
  Action,
  ActionStatus,
} from "@/types/action";

export interface ActionCardProps {
  action: Action;
  compact?: boolean;
  onClick?: (action: Action) => void;
  onApprove?: (action: Action) => void;
  onExecute?: (action: Action) => void;
  className?: string;
}

function actionVariant(
  status: ActionStatus,
): "yellow" | "lime" | "pink" | "cyan" | "orange" | "red" | "green" | "dark" | "outline" {
  switch (status) {
    case "completed":
      return "green";
    case "failed":
      return "red";
    case "rejected":
    case "cancelled":
      return "dark";
    case "awaiting_approval":
      return "orange";
    case "executing":
      return "cyan";
    case "approved":
      return "lime";
    default:
      return "yellow";
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

export function ActionCard({
  action,
  compact = false,
  onClick,
  onApprove,
  onExecute,
  className,
}: ActionCardProps) {
  const interactive = Boolean(onClick);

  const canApprove =
    action.requires_approval &&
    action.status ===
      "awaiting_approval" &&
    Boolean(onApprove);

  const canExecute =
    !action.requires_approval &&
    (action.status === "proposed" ||
      action.status === "approved") &&
    Boolean(onExecute);

  return (
    <Card
      variant={actionVariant(action.status)}
      className={cn(
        interactive &&
          "cursor-pointer transition-none hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[7px_7px_0_#000]",
        compact && "p-4",
        className,
      )}
      onClick={
        onClick
          ? () => onClick(action)
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
                onClick?.(action);
              }
            }
          : undefined
      }
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge
              variant="dark"
              size="sm"
            >
              {action.action_type}
            </Badge>

            <Badge
              variant={getStatusBadgeVariant(
                action.status,
              )}
              size="sm"
            >
              {action.status}
            </Badge>

            {action.requires_approval && (
              <Badge
                variant="orange"
                size="sm"
              >
                Approval required
              </Badge>
            )}
          </div>

          <h3 className="text-lg font-black uppercase leading-tight">
            {action.title ||
              action.action_type}
          </h3>

          <p className="mt-1 break-all font-mono text-[10px] font-black opacity-60">
            {action.action_id}
          </p>
        </div>

        {action.confidence !== null && (
          <div className="shrink-0 border-[2px] border-black bg-white px-3 py-2 text-center">
            <span className="block text-[9px] font-black uppercase">
              Confidence
            </span>

            <span className="text-lg font-black">
              {formatPercentage(
                action.confidence,
              )}
            </span>
          </div>
        )}
      </div>

      {action.description && (
        <p className="mt-4 text-sm font-bold leading-relaxed">
          {action.description}
        </p>
      )}

      {action.rationale && (
        <div className="mt-4 border-[3px] border-black bg-white p-3">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Rationale
          </span>

          <p className="mt-1 text-sm font-bold leading-relaxed">
            {action.rationale}
          </p>
        </div>
      )}

      <div className="mt-4 grid gap-3 border-t-[3px] border-black pt-4 sm:grid-cols-3">
        <div>
          <span className="block text-[9px] font-black uppercase opacity-60">
            Created
          </span>

          <span className="text-xs font-black">
            {formatDate(action.created_at)}
          </span>
        </div>

        <div>
          <span className="block text-[9px] font-black uppercase opacity-60">
            Updated
          </span>

          <span className="text-xs font-black">
            {formatDate(action.updated_at)}
          </span>
        </div>

        <div>
          <span className="block text-[9px] font-black uppercase opacity-60">
            Completed
          </span>

          <span className="text-xs font-black">
            {formatDate(
              action.completed_at,
            )}
          </span>
        </div>
      </div>

      {action.approval && (
        <div className="mt-4 border-[3px] border-black bg-[var(--orange)] p-3">
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs font-black uppercase">
              Approval
            </span>

            <Badge
              variant={
                action.approval.status ===
                "approved"
                  ? "green"
                  : action.approval.status ===
                      "rejected"
                    ? "red"
                    : "dark"
              }
              size="sm"
            >
              {action.approval.status}
            </Badge>
          </div>

          {action.approval.comment && (
            <p className="mt-2 text-xs font-bold leading-relaxed">
              {action.approval.comment}
            </p>
          )}

          {action.approval.approved_by && (
            <p className="mt-2 text-[10px] font-black uppercase">
              Approved by:{" "}
              {action.approval.approved_by}
            </p>
          )}
        </div>
      )}

      {action.evidence_ids.length > 0 && (
        <div className="mt-4">
          <span className="mb-2 block text-[10px] font-black uppercase">
            Evidence
          </span>

          <div className="flex flex-wrap gap-2">
            {action.evidence_ids.map(
              (evidenceId) => (
                <span
                  key={evidenceId}
                  className="border-[2px] border-black bg-white px-2 py-1 font-mono text-[10px] font-black"
                >
                  {evidenceId}
                </span>
              ),
            )}
          </div>
        </div>
      )}

      {action.result && (
        <div className="mt-4 border-[3px] border-black bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[10px] font-black uppercase">
              Execution result
            </span>

            <Badge
              variant={
                action.result.success
                  ? "green"
                  : "red"
              }
              size="sm"
            >
              {action.result.status}
            </Badge>
          </div>

          {action.result.message && (
            <p className="mt-2 text-sm font-bold">
              {action.result.message}
            </p>
          )}

          {action.result.error && (
            <p className="mt-2 border-[2px] border-black bg-[var(--red)] p-2 text-xs font-black">
              {action.result.error}
            </p>
          )}

          {Object.keys(
            action.result.data,
          ).length > 0 && (
            <details className="mt-3 border-[2px] border-black">
              <summary className="cursor-pointer px-3 py-2 text-[10px] font-black uppercase">
                Result data
              </summary>

              <pre className="overflow-x-auto whitespace-pre-wrap break-words border-t-[2px] border-black bg-[var(--bg)] p-3 font-mono text-[10px] font-bold">
                {JSON.stringify(
                  action.result.data,
                  null,
                  2,
                )}
              </pre>
            </details>
          )}
        </div>
      )}

      {(canApprove || canExecute) && (
        <div
          className="mt-4 flex flex-wrap gap-2 border-t-[3px] border-black pt-4"
          onClick={(event) =>
            event.stopPropagation()
          }
        >
          {canApprove && (
            <button
              type="button"
              className="neo-button neo-button-orange"
              onClick={() =>
                onApprove?.(action)
              }
            >
              Approve Action
            </button>
          )}

          {canExecute && (
            <button
              type="button"
              className="neo-button neo-button-green"
              onClick={() =>
                onExecute?.(action)
              }
            >
              Execute Action
            </button>
          )}
        </div>
      )}
    </Card>
  );
}

export default ActionCard;