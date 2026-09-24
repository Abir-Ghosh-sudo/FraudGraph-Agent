"use client";

import { cn } from "@/lib/utils";

import {
  Badge,
  getStatusBadgeVariant,
} from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { Card } from "@/components/common/card";
import type { Action } from "@/types/action";

export interface NextBestActionProps {
  action: Action | null | undefined;
  onSelect?: (action: Action) => void;
  onApprove?: (action: Action) => void;
  onExecute?: (action: Action) => void;
  loading?: boolean;
  compact?: boolean;
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

function actionRequiresApproval(
  action: Action,
): boolean {
  return (
    action.requires_approval ||
    action.status === "awaiting_approval"
  );
}

export function NextBestAction({
  action,
  onSelect,
  onApprove,
  onExecute,
  loading = false,
  compact = false,
  className,
}: NextBestActionProps) {
  if (!action) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <div className="flex items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">
              Next best action
            </span>

            <p className="mt-1 text-sm font-black uppercase">
              No recommendation available
            </p>
          </div>

          <Badge
            variant="outline"
            size="sm"
          >
            No data
          </Badge>
        </div>
      </Card>
    );
  }

  const requiresApproval =
    actionRequiresApproval(action);

  const canApprove =
    requiresApproval &&
    action.status ===
      "awaiting_approval" &&
    Boolean(onApprove);

  const canExecute =
    !requiresApproval &&
    (action.status === "proposed" ||
      action.status === "approved") &&
    Boolean(onExecute);

  return (
    <Card
      variant="yellow"
      className={cn(
        "relative overflow-hidden",
        compact && "p-4",
        className,
      )}
      onClick={
        onSelect
          ? () => onSelect(action)
          : undefined
      }
      role={
        onSelect ? "button" : undefined
      }
      tabIndex={onSelect ? 0 : undefined}
      onKeyDown={
        onSelect
          ? (event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                event.preventDefault();
                onSelect(action);
              }
            }
          : undefined
      }
    >
      <div className="absolute right-0 top-0 border-l-[3px] border-b-[3px] border-black bg-[var(--pink)] px-3 py-2">
        <span className="text-[9px] font-black uppercase">
          Recommended action
        </span>
      </div>

      <div className="pr-32">
        <div className="flex flex-wrap items-center gap-2">
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

          {requiresApproval && (
            <Badge
              variant="orange"
              size="sm"
            >
              Approval required
            </Badge>
          )}
        </div>

        <h3 className="mt-3 text-2xl font-black uppercase leading-tight">
          {action.title ||
            action.action_type}
        </h3>

        <p className="mt-1 break-all font-mono text-[10px] font-black opacity-50">
          {action.action_id}
        </p>
      </div>

      {action.description && (
        <p className="mt-4 max-w-3xl text-sm font-bold leading-relaxed">
          {action.description}
        </p>
      )}

      {action.rationale && (
        <div className="mt-4 border-[3px] border-black bg-white p-4">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Why this action
          </span>

          <p className="mt-1 text-sm font-bold leading-relaxed">
            {action.rationale}
          </p>
        </div>
      )}

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Metric
          label="Confidence"
          value={formatPercentage(
            action.confidence,
          )}
        />

        <Metric
          label="Evidence"
          value={String(
            action.evidence_ids.length,
          )}
        />

        <Metric
          label="Approval"
          value={
            requiresApproval
              ? "Required"
              : "Not required"
          }
        />
      </div>

      {action.evidence_ids.length > 0 && (
        <div className="mt-4 border-t-[3px] border-black pt-4">
          <span className="block text-[10px] font-black uppercase">
            Supporting evidence
          </span>

          <div className="mt-2 flex flex-wrap gap-2">
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

      {(canApprove || canExecute) && (
        <div
          className="mt-5 flex flex-wrap gap-3 border-t-[3px] border-black pt-4"
          onClick={(event) =>
            event.stopPropagation()
          }
        >
          {canApprove && (
            <Button
              type="button"
              variant="orange"
              loading={loading}
              disabled={loading}
              onClick={() =>
                onApprove?.(action)
              }
            >
              Approve Action
            </Button>
          )}

          {canExecute && (
            <Button
              type="button"
              variant="dark"
              loading={loading}
              disabled={loading}
              onClick={() =>
                onExecute?.(action)
              }
            >
              Execute Action
            </Button>
          )}
        </div>
      )}

      {action.result && (
        <div className="mt-4 border-[3px] border-black bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[10px] font-black uppercase">
              Latest result
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
            <p className="mt-2 text-xs font-bold leading-relaxed">
              {action.result.message}
            </p>
          )}
        </div>
      )}
    </Card>
  );
}

interface MetricProps {
  label: string;
  value: string;
}

function Metric({
  label,
  value,
}: MetricProps) {
  return (
    <div className="border-[2px] border-black bg-white p-3">
      <span className="block text-[9px] font-black uppercase opacity-60">
        {label}
      </span>

      <span className="mt-1 block text-lg font-black uppercase">
        {value}
      </span>
    </div>
  );
}

export default NextBestAction;