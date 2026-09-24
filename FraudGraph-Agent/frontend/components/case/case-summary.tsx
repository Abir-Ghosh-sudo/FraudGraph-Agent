import { cn } from "@/lib/utils";

import {
  Badge,
  RiskBadge,
  StatusBadge,
} from "@/components/common/badge";
import { Card } from "@/components/common/card";
import { RiskScore } from "@/components/risk/risk-score";
import type { Case } from "@/types/case";

export interface CaseSummaryProps {
  caseData: Case;
  compact?: boolean;
  onInvestigationClick?: (
    investigationId: string,
  ) => void;
  onTransactionClick?: (
    transactionId: string,
  ) => void;
  onCustomerClick?: (
    customerId: string,
  ) => void;
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

function formatOutcome(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    );
}

export function CaseSummary({
  caseData,
  compact = false,
  onInvestigationClick,
  onTransactionClick,
  onCustomerClick,
  className,
}: CaseSummaryProps) {
  return (
    <Card
      variant="default"
      className={cn(
        compact && "p-4",
        className,
      )}
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge
              status={caseData.status}
              size="sm"
            />

            <RiskBadge
              riskLevel={caseData.risk_level}
              size="sm"
            />

            {caseData.outcome && (
              <Badge
                variant="dark"
                size="sm"
              >
                {formatOutcome(
                  caseData.outcome,
                )}
              </Badge>
            )}
          </div>

          <h2 className="mt-3 break-words text-2xl font-black uppercase leading-tight sm:text-3xl">
            {caseData.title}
          </h2>

          <p className="mt-1 break-all font-mono text-[10px] font-black opacity-50">
            {caseData.case_id}
          </p>

          {caseData.description && (
            <p className="mt-4 max-w-3xl text-sm font-bold leading-relaxed">
              {caseData.description}
            </p>
          )}
        </div>

        <div className="w-full shrink-0 sm:w-auto lg:min-w-52">
          <RiskScore
            score={caseData.risk_score}
            level={caseData.risk_level}
            compact
          />
        </div>
      </div>

      <div className="mt-5 grid gap-3 border-t-[3px] border-black pt-5 sm:grid-cols-2 lg:grid-cols-4">
        <ReferenceField
          label="Investigation"
          value={caseData.investigation_id}
          onClick={
            onInvestigationClick
          }
        />

        <ReferenceField
          label="Transaction"
          value={caseData.transaction_id}
          onClick={
            onTransactionClick
          }
        />

        <ReferenceField
          label="Customer"
          value={caseData.customer_id}
          onClick={onCustomerClick}
        />

        <InfoField
          label="Account"
          value={caseData.account_id}
        />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Evidence"
          value={caseData.evidence_ids.length}
        />

        <Stat
          label="Findings"
          value={caseData.findings.length}
        />

        <Stat
          label="Decisions"
          value={caseData.decisions.length}
        />

        <Stat
          label="Actions"
          value={caseData.actions.length}
        />
      </div>

      <div className="mt-5 grid gap-3 border-t-[3px] border-black pt-5 sm:grid-cols-2 lg:grid-cols-4">
        <InfoField
          label="Fraud type"
          value={caseData.fraud_type}
        />

        <InfoField
          label="Created"
          value={formatDate(
            caseData.created_at,
          )}
        />

        <InfoField
          label="Updated"
          value={formatDate(
            caseData.updated_at,
          )}
        />

        <InfoField
          label="Resolved"
          value={formatDate(
            caseData.resolved_at,
          )}
        />
      </div>
    </Card>
  );
}

interface InfoFieldProps {
  label: string;
  value: string | number | null | undefined;
}

function InfoField({
  label,
  value,
}: InfoFieldProps) {
  return (
    <div className="border-[2px] border-black bg-[var(--bg)] p-3">
      <span className="block text-[9px] font-black uppercase opacity-50">
        {label}
      </span>

      <span className="mt-1 block break-words text-xs font-black">
        {value || "—"}
      </span>
    </div>
  );
}

interface ReferenceFieldProps {
  label: string;
  value: string | null | undefined;
  onClick?: (
    value: string,
  ) => void;
}

function ReferenceField({
  label,
  value,
  onClick,
}: ReferenceFieldProps) {
  const interactive =
    Boolean(value && onClick);

  if (!value) {
    return (
      <InfoField
        label={label}
        value={null}
      />
    );
  }

  if (!interactive) {
    return (
      <InfoField
        label={label}
        value={value}
      />
    );
  }

  return (
    <button
      type="button"
      onClick={() =>
        onClick?.(value)
      }
      className="border-[2px] border-black bg-[var(--bg)] p-3 text-left transition-none hover:bg-[var(--yellow)]"
    >
      <span className="block text-[9px] font-black uppercase opacity-50">
        {label}
      </span>

      <span className="mt-1 block break-all font-mono text-xs font-black underline decoration-[2px] underline-offset-2">
        {value}
      </span>
    </button>
  );
}

interface StatProps {
  label: string;
  value: number;
}

function Stat({
  label,
  value,
}: StatProps) {
  return (
    <div className="border-[3px] border-black bg-white p-3 shadow-[3px_3px_0_#000]">
      <span className="block text-[9px] font-black uppercase opacity-50">
        {label}
      </span>

      <span className="mt-1 block text-2xl font-black">
        {value}
      </span>
    </div>
  );
}

export default CaseSummary;