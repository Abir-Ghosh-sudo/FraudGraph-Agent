"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

import {
  Badge,
  getStatusBadgeVariant,
} from "@/components/common/badge";
import { Button } from "@/components/common/button";
import { Card } from "@/components/common/card";
import type {
  Action,
  ActionApproval,
  ApprovalStatus,
} from "@/types/action";

export interface ApprovalCardProps {
  action?: Action | null;
  approval?: ActionApproval | null;
  onApprove?: (
    action: Action,
    comment?: string,
  ) => Promise<void> | void;
  onReject?: (
    action: Action,
    comment?: string,
  ) => Promise<void> | void;
  loading?: boolean;
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

function isPending(status: ApprovalStatus) {
  return status === "pending";
}

export function ApprovalCard({
  action,
  approval,
  onApprove,
  onReject,
  loading = false,
  compact = false,
  className,
}: ApprovalCardProps) {
  const [comment, setComment] =
    useState("");

  if (!approval) {
    return (
      <Card
        variant="default"
        className={cn(
          "border-dashed",
          className,
        )}
      >
        <p className="text-sm font-black uppercase opacity-60">
          No approval record available
        </p>
      </Card>
    );
  }

  const pending =
    isPending(approval.status);

  const canDecide =
    pending &&
    Boolean(action) &&
    Boolean(onApprove || onReject);

  const handleApprove = async () => {
    if (!action || !onApprove) {
      return;
    }

    await onApprove(
      action,
      comment.trim() || undefined,
    );
  };

  const handleReject = async () => {
    if (!action || !onReject) {
      return;
    }

    await onReject(
      action,
      comment.trim() || undefined,
    );
  };

  return (
    <Card
      variant={
        pending ? "orange" : "default"
      }
      className={cn(
        compact && "p-4",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.14em]">
            Approval request
          </span>

          <h3 className="mt-1 text-xl font-black uppercase">
            Human approval required
          </h3>

          <p className="mt-1 break-all font-mono text-[10px] font-black opacity-60">
            {approval.approval_id}
          </p>
        </div>

        <Badge
          variant={getStatusBadgeVariant(
            approval.status,
          )}
          size="md"
        >
          {approval.status}
        </Badge>
      </div>

      {action && (
        <div className="mt-4 border-[3px] border-black bg-white p-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="dark"
              size="sm"
            >
              {action.action_type}
            </Badge>

            <span className="font-mono text-[10px] font-black opacity-60">
              {action.action_id}
            </span>
          </div>

          {action.title && (
            <h4 className="mt-2 text-base font-black uppercase">
              {action.title}
            </h4>
          )}

          {action.rationale && (
            <p className="mt-2 text-sm font-bold leading-relaxed">
              {action.rationale}
            </p>
          )}
        </div>
      )}

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <InfoField
          label="Requested by"
          value={
            approval.requested_by
          }
        />

        <InfoField
          label="Requested at"
          value={formatDate(
            approval.requested_at,
          )}
        />

        <InfoField
          label="Approved by"
          value={
            approval.approved_by
          }
        />

        <InfoField
          label="Decided at"
          value={formatDate(
            approval.decided_at,
          )}
        />
      </div>

      {approval.comment && (
        <div className="mt-4 border-[3px] border-black bg-white p-4">
          <span className="block text-[10px] font-black uppercase opacity-60">
            Decision comment
          </span>

          <p className="mt-1 text-sm font-bold leading-relaxed">
            {approval.comment}
          </p>
        </div>
      )}

      {canDecide && (
        <div className="mt-4 border-t-[3px] border-black pt-4">
          <label
            htmlFor={`approval-comment-${approval.approval_id}`}
            className="neo-label"
          >
            Decision comment
          </label>

          <textarea
            id={`approval-comment-${approval.approval_id}`}
            value={comment}
            onChange={(event) =>
              setComment(event.target.value)
            }
            placeholder="Add an optional decision comment..."
            disabled={loading}
            rows={3}
            className="neo-input mt-2 min-h-24 resize-y"
          />

          <div className="mt-3 flex flex-wrap gap-3">
            {onApprove && (
              <Button
                type="button"
                variant="lime"
                loading={loading}
                disabled={loading}
                onClick={handleApprove}
              >
                Approve
              </Button>
            )}

            {onReject && (
              <Button
                type="button"
                variant="danger"
                loading={loading}
                disabled={loading}
                onClick={handleReject}
              >
                Reject
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}

interface InfoFieldProps {
  label: string;
  value: string | null | undefined;
}

function InfoField({
  label,
  value,
}: InfoFieldProps) {
  return (
    <div className="border-[2px] border-black bg-white p-3">
      <span className="block text-[9px] font-black uppercase opacity-60">
        {label}
      </span>

      <span className="mt-1 block break-words text-xs font-black">
        {value || "—"}
      </span>
    </div>
  );
}

export default ApprovalCard;