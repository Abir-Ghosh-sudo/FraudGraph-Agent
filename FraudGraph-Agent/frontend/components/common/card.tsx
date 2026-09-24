import type {
  HTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";

export type CardVariant =
  | "default"
  | "yellow"
  | "lime"
  | "pink"
  | "cyan"
  | "orange"
  | "dark"
  | "red"
  | "green"
  | "outline";

export interface CardProps
  extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  interactive?: boolean;
}

const variantClasses: Record<
  CardVariant,
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

  dark:
    "bg-black text-white",

  red:
    "bg-[var(--red)] text-black",

  green:
    "bg-[var(--green)] text-black",

  outline:
    "bg-transparent text-black",
};

export function Card({
  variant = "default",
  interactive = false,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "neo-card",
        "border-[3px] border-black",
        "shadow-[6px_6px_0_#000]",
        "overflow-hidden",
        variantClasses[variant],
        interactive && [
          "cursor-pointer",
          "transition-none",
          "hover:translate-x-[2px]",
          "hover:translate-y-[2px]",
          "hover:shadow-[4px_4px_0_#000]",
        ],
        className,
      )}
      {...props}
    />
  );
}

export interface CardHeaderProps
  extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  action?: ReactNode;
}

export function CardHeader({
  title,
  description,
  action,
  className,
  children,
  ...props
}: CardHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3",
        "border-b-[3px] border-black",
        "p-4 sm:p-5",
        "sm:flex-row sm:items-start sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">
        {title && (
          <h3 className="text-lg font-black uppercase leading-tight tracking-tight">
            {title}
          </h3>
        )}

        {description && (
          <p className="mt-1 text-sm font-bold leading-relaxed opacity-70">
            {description}
          </p>
        )}

        {children}
      </div>

      {action && (
        <div className="shrink-0">
          {action}
        </div>
      )}
    </div>
  );
}

export function CardContent({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "p-4 sm:p-5",
        className,
      )}
      {...props}
    />
  );
}

export function CardFooter({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-3",
        "border-t-[3px] border-black",
        "p-4 sm:p-5",
        className,
      )}
      {...props}
    />
  );
}

export interface StatCardProps
  extends Omit<CardProps, "children"> {
  label: string;
  value: ReactNode;
  description?: string;
  icon?: ReactNode;
}

export function StatCard({
  label,
  value,
  description,
  icon,
  variant = "default",
  className,
  ...props
}: StatCardProps) {
  return (
    <Card
      variant={variant}
      className={cn(
        "min-h-[150px]",
        className,
      )}
      {...props}
    >
      <div className="flex h-full flex-col justify-between gap-6 p-5">
        <div className="flex items-start justify-between gap-4">
          <span className="text-xs font-black uppercase tracking-[0.12em]">
            {label}
          </span>

          {icon && (
            <span className="text-xl">
              {icon}
            </span>
          )}
        </div>

        <div>
          <div className="text-3xl font-black leading-none sm:text-4xl">
            {value}
          </div>

          {description && (
            <p className="mt-2 text-xs font-bold opacity-70">
              {description}
            </p>
          )}
        </div>
      </div>
    </Card>
  );
}

export default Card;