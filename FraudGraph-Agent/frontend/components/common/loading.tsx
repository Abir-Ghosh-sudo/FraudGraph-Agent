import type { ReactNode } from "react";

import { Button } from "@/components/common/button";
import { cn } from "@/lib/utils";

export interface LoadingProps {
  label?: string;
  className?: string;
  fullHeight?: boolean;
}

export function Loading({
  label = "Loading...",
  className,
  fullHeight = false,
}: LoadingProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "flex items-center justify-center",
        fullHeight && "min-h-[280px]",
        className,
      )}
    >
      <div className="neo-loading flex items-center gap-3 border-[3px] border-black bg-[var(--yellow)] px-5 py-4 shadow-[5px_5px_0_#000]">
        <span
          aria-hidden="true"
          className="h-5 w-5 animate-spin border-[4px] border-black border-r-transparent"
        />

        <span className="text-sm font-black uppercase">
          {label}
        </span>
      </div>
    </div>
  );
}

export interface LoadingBlockProps {
  lines?: number;
  className?: string;
}

export function LoadingBlock({
  lines = 3,
  className,
}: LoadingBlockProps) {
  return (
    <div
      role="status"
      aria-label="Loading content"
      className={cn(
        "space-y-3",
        className,
      )}
    >
      {Array.from({
        length: Math.max(1, lines),
      }).map((_, index) => (
        <div
          key={index}
          className={cn(
            "h-4 animate-pulse",
            "border-[2px] border-black",
            "bg-[var(--cyan)]",
            index === lines - 1 &&
              "w-2/3",
          )}
        />
      ))}
    </div>
  );
}

export interface ErrorStateProps {
  title?: string;
  message?: string | null;
  onRetry?: () => void | Promise<void>;
  retryLabel?: string;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  message = "The requested data could not be loaded.",
  onRetry,
  retryLabel = "Retry",
  className,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        "neo-error",
        "border-[3px] border-black",
        "bg-[var(--red)] text-black",
        "p-5 shadow-[6px_6px_0_#000]",
        className,
      )}
    >
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-lg font-black uppercase">
            {title}
          </h3>

          {message && (
            <p className="mt-2 text-sm font-bold leading-relaxed">
              {message}
            </p>
          )}
        </div>

        {onRetry && (
          <div>
            <Button
              variant="dark"
              onClick={() => {
                void onRetry();
              }}
            >
              {retryLabel}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

export interface EmptyStateProps {
  title?: string;
  message?: string;
  action?: ReactNode;
  icon?: ReactNode;
  className?: string;
}

export function EmptyState({
  title = "No data found",
  message = "There is nothing to display here yet.",
  action,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "neo-empty",
        "flex min-h-[220px] flex-col items-center justify-center",
        "border-[3px] border-dashed border-black",
        "bg-white p-6 text-center",
        className,
      )}
    >
      {icon && (
        <div
          aria-hidden="true"
          className="mb-4 text-4xl"
        >
          {icon}
        </div>
      )}

      <h3 className="text-xl font-black uppercase">
        {title}
      </h3>

      <p className="mt-2 max-w-md text-sm font-bold leading-relaxed opacity-70">
        {message}
      </p>

      {action && (
        <div className="mt-5">
          {action}
        </div>
      )}
    </div>
  );
}

export interface PageStateProps {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyTitle?: string;
  emptyMessage?: string;
  onRetry?: () => void | Promise<void>;
  children: ReactNode;
}

export function PageState({
  loading = false,
  error = null,
  empty = false,
  emptyTitle,
  emptyMessage,
  onRetry,
  children,
}: PageStateProps) {
  if (loading) {
    return <Loading fullHeight />;
  }

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={onRetry}
      />
    );
  }

  if (empty) {
    return (
      <EmptyState
        title={emptyTitle}
        message={emptyMessage}
      />
    );
  }

  return <>{children}</>;
}

export default Loading;