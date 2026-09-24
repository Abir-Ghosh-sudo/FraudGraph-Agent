import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export type BadgeVariant =
  | "default"
  | "yellow"
  | "lime"
  | "pink"
  | "cyan"
  | "orange"
  | "red"
  | "green"
  | "dark"
  | "outline";

export type BadgeSize =
  | "sm"
  | "md"
  | "lg";

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
}

const variantClasses: Record<
  BadgeVariant,
  string
> = {
  default:
    "bg-white text-black",

  yellow:
    "bg-[var(--yellow)] text-black",

  lime:
    "bg-[var(--lime)] text-black",

  pink:
    "bg-[var(--pink)] text-black",

  cyan:
    "bg-[var(--cyan)] text-black",

  orange:
    "bg-[var(--orange)] text-black",

  red:
    "bg-[var(--red)] text-black",

  green:
    "bg-[var(--green)] text-black",

  dark:
    "bg-[var(--ink)] text-white",

  outline:
    "bg-transparent text-black",
};

const sizeClasses: Record<
  BadgeSize,
  string
> = {
  sm:
    "px-2 py-0.5 text-[10px] min-h-[22px]",

  md:
    "px-2.5 py-1 text-xs min-h-[26px]",

  lg:
    "px-3 py-1.5 text-sm min-h-[30px]",
};

export function Badge({
  variant = "default",
  size = "md",
  className,
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "neo-badge",
        "inline-flex items-center justify-center",
        "w-fit whitespace-nowrap",
        "font-black uppercase tracking-[0.04em]",
        "border-[3px] border-black",
        "shadow-[3px_3px_0_#000]",
        "leading-none",
        variantClasses[variant],
        sizeClasses[size],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}

function normalizeValue(
  value: string | null | undefined,
): string {
  return (
    value
      ?.trim()
      .toLowerCase()
      .replace(/[\s-]+/g, "_") ?? ""
  );
}

export function getStatusBadgeVariant(
  status: string | null | undefined,
): BadgeVariant {
  switch (normalizeValue(status)) {
    case "completed":
    case "approved":
    case "resolved":
    case "closed":
    case "actioned":
    case "confirmed":
    case "confirmed_fraud":
      return "green";

    case "running":
    case "investigating":
    case "processing":
    case "executing":
    case "pending":
      return "cyan";

    case "awaiting_approval":
    case "awaiting_evidence":
    case "proposed":
    case "monitor":
      return "yellow";

    case "failed":
    case "rejected":
    case "cancelled":
    case "error":
      return "red";

    case "escalated":
    case "critical":
      return "pink";

    case "high":
      return "orange";

    case "medium":
      return "yellow";

    case "low":
      return "lime";

    default:
      return "default";
  }
}

export function getRiskBadgeVariant(
  riskLevel: string | null | undefined,
): BadgeVariant {
  switch (normalizeValue(riskLevel)) {
    case "critical":
      return "red";

    case "high":
      return "orange";

    case "medium":
      return "yellow";

    case "low":
      return "lime";

    case "unknown":
    default:
      return "default";
  }
}

export interface StatusBadgeProps
  extends Omit<BadgeProps, "variant"> {
  status: string | null | undefined;
}

export function StatusBadge({
  status,
  children,
  ...props
}: StatusBadgeProps) {
  return (
    <Badge
      variant={getStatusBadgeVariant(status)}
      {...props}
    >
      {children ?? status ?? "Unknown"}
    </Badge>
  );
}

export interface RiskBadgeProps
  extends Omit<BadgeProps, "variant"> {
  riskLevel: string | null | undefined;
}

export function RiskBadge({
  riskLevel,
  children,
  ...props
}: RiskBadgeProps) {
  return (
    <Badge
      variant={getRiskBadgeVariant(riskLevel)}
      {...props}
    >
      {children ?? riskLevel ?? "Unknown"}
    </Badge>
  );
}

export default Badge;