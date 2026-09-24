import { cn } from "@/lib/utils";

import { Badge } from "@/components/common/badge";
import type {
  Case,
  CaseAction,
  CaseDecision,
  CaseFinding,
} from "@/types/case";

type TimelineEventType =
  | "created"
  | "updated"
  | "resolved"
  | "closed"
  | "finding"
  | "decision"
  | "action";

interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  title: string;
  description: string | null;
  timestamp: string;
  badge: string;
  variant:
    | "yellow"
    | "lime"
    | "pink"
    | "cyan"
    | "orange"
    | "red"
    | "green"
    | "dark"
    | "outline";
  evidenceIds: string[];
}

export interface CaseTimelineProps {
  caseData: Case;
  compact?: boolean;
  maxItems?: number;
  className?: string;
}

function formatDate(
  value: string,
): string {
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

function buildTimeline(
  caseData: Case,
): TimelineEvent[] {
  const events: TimelineEvent[] = [];

  events.push({
    id: `case-created-${caseData.case_id}`,
    type: "created",
    title: "Case created",
    description:
      caseData.description,
    timestamp: caseData.created_at,
    badge: "Created",
    variant: "cyan",
    evidenceIds: [],
  });

  for (const finding of caseData.findings) {
    events.push(
      findingToEvent(finding),
    );
  }

  for (const decision of caseData.decisions) {
    events.push(
      decisionToEvent(decision),
    );
  }

  for (const action of caseData.actions) {
    events.push(
      actionToEvent(action),
    );
  }

  if (
    caseData.updated_at &&
    caseData.updated_at !==
      caseData.created_at
  ) {
    events.push({
      id: `case-updated-${caseData.case_id}-${caseData.updated_at}`,
      type: "updated",
      title: "Case updated",
      description: `Current status: ${caseData.status}`,
      timestamp: caseData.updated_at,
      badge: "Updated",
      variant: "yellow",
      evidenceIds:
        caseData.evidence_ids,
    });
  }

  if (caseData.resolved_at) {
    events.push({
      id: `case-resolved-${caseData.case_id}`,
      type: "resolved",
      title: "Case resolved",
      description: caseData.outcome
        ? `Outcome: ${formatLabel(
            caseData.outcome,
          )}`
        : null,
      timestamp: caseData.resolved_at,
      badge: "Resolved",
      variant: "green",
      evidenceIds:
        caseData.evidence_ids,
    });
  }

  if (caseData.closed_at) {
    events.push({
      id: `case-closed-${caseData.case_id}`,
      type: "closed",
      title: "Case closed",
      description: null,
      timestamp: caseData.closed_at,
      badge: "Closed",
      variant: "dark",
      evidenceIds:
        caseData.evidence_ids,
    });
  }

  return events.sort(
    (a, b) =>
      new Date(
        b.timestamp,
      ).getTime() -
      new Date(
        a.timestamp,
      ).getTime(),
  );
}

function findingToEvent(
  finding: CaseFinding,
): TimelineEvent {
  return {
    id: `finding-${finding.finding_id}`,
    type: "finding",
    title: finding.title,
    description:
      finding.description,
    timestamp: finding.created_at,
    badge: "Finding",
    variant: "pink",
    evidenceIds:
      finding.evidence_ids,
  };
}

function decisionToEvent(
  decision: CaseDecision,
): TimelineEvent {
  const approval =
    decision.requires_approval
      ? decision.approved === true
        ? "Approved"
        : decision.approved === false
          ? "Rejected"
          : "Approval pending"
      : "No approval";

  return {
    id: `decision-${decision.decision_id}`,
    type: "decision",
    title: formatLabel(
      decision.decision_type,
    ),
    description: `${decision.rationale} • ${approval}`,
    timestamp: decision.created_at,
    badge: "Decision",
    variant: "orange",
    evidenceIds:
      decision.evidence_ids,
  };
}

function actionToEvent(
  action: CaseAction,
): TimelineEvent {
  return {
    id: `action-${action.action_id}`,
    type: "action",
    title: formatLabel(
      action.action_type,
    ),
    description:
      action.rationale ||
      `Action status: ${action.status}`,
    timestamp: action.created_at,
    badge: "Action",
    variant:
      action.status === "failed"
        ? "red"
        : action.status === "completed"
          ? "green"
          : "lime",
    evidenceIds: [],
  };
}

function formatLabel(
  value: string,
): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    );
}

export function CaseTimeline({
  caseData,
  compact = false,
  maxItems,
  className,
}: CaseTimelineProps) {
  const timeline =
    buildTimeline(caseData);

  const visibleEvents =
    typeof maxItems === "number"
      ? timeline.slice(0, maxItems)
      : timeline;

  return (
    <section
      className={cn(
        "border-[3px] border-black bg-[var(--surface)] p-5 shadow-[6px_6px_0_#000]",
        compact && "p-4",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-[0.14em] opacity-60">
            Case activity
          </span>

          <h2 className="mt-1 text-xl font-black uppercase">
            Investigation Timeline
          </h2>
        </div>

        <Badge
          variant="dark"
          size="sm"
        >
          {timeline.length} events
        </Badge>
      </div>

      {visibleEvents.length === 0 ? (
        <div className="mt-5 border-[2px] border-dashed border-black p-5">
          <p className="text-sm font-black uppercase opacity-60">
            No timeline events available
          </p>
        </div>
      ) : (
        <div className="relative mt-6">
          <div className="absolute bottom-2 left-[9px] top-2 w-[3px] bg-black" />

          <div className="space-y-5">
            {visibleEvents.map(
              (event) => (
                <TimelineItem
                  key={event.id}
                  event={event}
                />
              ),
            )}
          </div>
        </div>
      )}
    </section>
  );
}

interface TimelineItemProps {
  event: TimelineEvent;
}

function TimelineItem({
  event,
}: TimelineItemProps) {
  return (
    <article className="relative pl-8">
      <div
        className={cn(
          "absolute left-0 top-1 h-5 w-5 border-[3px] border-black",
          event.variant === "pink" &&
            "bg-[var(--pink)]",
          event.variant === "cyan" &&
            "bg-[var(--cyan)]",
          event.variant === "yellow" &&
            "bg-[var(--yellow)]",
          event.variant === "orange" &&
            "bg-[var(--orange)]",
          event.variant === "lime" &&
            "bg-[var(--lime)]",
          event.variant === "green" &&
            "bg-[var(--green)]",
          event.variant === "red" &&
            "bg-[var(--red)]",
          event.variant === "dark" &&
            "bg-black",
          event.variant === "outline" &&
            "bg-white",
        )}
      />

      <div className="border-[3px] border-black bg-white p-4 shadow-[3px_3px_0_#000]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <Badge
              variant={event.variant}
              size="sm"
            >
              {event.badge}
            </Badge>

            <h3 className="mt-2 text-sm font-black uppercase">
              {event.title}
            </h3>
          </div>

          <time className="text-[10px] font-black uppercase opacity-50">
            {formatDate(event.timestamp)}
          </time>
        </div>

        {event.description && (
          <p className="mt-3 text-xs font-bold leading-relaxed">
            {event.description}
          </p>
        )}

        {event.evidenceIds.length > 0 && (
          <div className="mt-3 border-t-[2px] border-black pt-3">
            <span className="block text-[9px] font-black uppercase opacity-50">
              Evidence
            </span>

            <div className="mt-2 flex flex-wrap gap-2">
              {event.evidenceIds.map(
                (evidenceId) => (
                  <span
                    key={evidenceId}
                    className="border-[2px] border-black bg-[var(--bg)] px-2 py-1 font-mono text-[9px] font-black"
                  >
                    {evidenceId}
                  </span>
                ),
              )}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}

export default CaseTimeline;